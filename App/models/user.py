from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import UserMixin
from sqlalchemy.sql.expression import func
from App.database import db


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False, unique=True)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String(120), nullable=False)

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.set_password(password)

    def get_json(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email
        }

    def set_password(self, password):
        """Create hashed password."""
        self.password = generate_password_hash(password, method='sha256')

    def check_password(self, password):
        """Check hashed password."""
        return check_password_hash(self.password, password)

    def __repr__(self):
        return f'<User {self.username} - {self.email}>'

class Chat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('regular_user.id'), nullable=False)
    text = db.Column(db.String(250), nullable=False)
    active = db.Column(db.Boolean, default=False)

    def __init__(self, text):
        self.text = text

    def toggle(self):
        self.done = not self.done
        db.session.add(self)
        db.session.commit()

    def cat_list(self):
        return ', '.join([category.text for category in self.categories])

    def toJSON(self):
        return {
            "id": self.id,
            "text": self.text,
            "done": self.done
        }

    def __repr__(self):
        return f'<Chat: {self.id} | {self.user.username} | {self.text} | {"active" if self.done else "not active"} | categories{self.cat_list()}>'

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('regular_user.id'), nullable=False)
    text = db.Column(db.String(255), nullable=False)
    user = db.relationship('RegularUser', backref=db.backref('categories', lazy='joined'))
    chats = db.relationship('Chat', secondary='chat_category', backref=db.backref('categories', lazy=True))

    def __init__(self, user_id, text):
        self.user_id = user_id
        self.text = text

    def __repr__(self):
        return f'<Category user: {self.user.username} - {self.text}>'

    def toJSON(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "user": self.user.username,
            "text": self.text
        }

class ChatCategory(db.Model):
    __tablename__ = 'chat_category'
    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.Integer, db.ForeignKey('chat.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    last_modified = db.Column(db.DateTime, default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f'<ChatCategory last modified {self.last_modified.strftime("%Y/%m/%d, %H:%m:%s")}>'

class RegularUser(User):
    __tablename__ = 'regular_user'
    chats = db.relationship('Chat', backref='user', lazy=True)

    def add_chat(self, text):
        new_chat = Chat(text=text)
        new_chat.user_id = self.id
        self.chats.append(new_chat)
        db.session.add(self)
        db.session.commit()
        return new_chat

    def delete_chat(self, chat_id):
        chat = Chat.query.filter_by(id=chat_id, user_id=self.id).first()
        if chat:
            db.session.delete(chat)
            db.session.commit()
            return True
        return None

    def update_chat(self, chat_id, text):
        chat = Chat.query.filter_by(id=chat_id, chat_id=self.id).first()
        if chat:
            chat.text = text
            db.session.add(chat)
            db.session.commit()
            return chat
        return None

    def add_chat_category(self, chat_id, category_text):
        category = Category.query.filter_by(text=category_text).first()
        chat = Chat.query.filter_by(id=chat_id, chat_id=self.id).first()
        if not chat:
            return None
        if not category:
            category = Category(self.id, category_text)
            db.session.add(category)
            db.session.commit()
        if category not in chat.categories:
            category.chats.append(chat)
            db.session.add(category)
            db.session.commit()
            return category

    def getNumChats(self):
        return len(self.chats)

    def getChatSent(self):
        chatSent = 0
        for chat in self.chats:
            if chat.done:
                chatSent += 1
        return chatSent

    def toJson(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email
        }

    def __repr__(self):
        return f'<RegularUser {self.id} : {self.username} - {self.email}>'

class Admin(User):
    __tablename__ = 'Admin'
    admin_id = db.Column(db.String(120), unique=True, nullable=False)

    def get_all_chats_json(self):
        chats = Chat.query.all()
        if chats:
            return [chat.get_json() for chat in chats]
        else:
            return []

    def get_all_chats(self):
        return Chat.query.all()

    def search_chats(self, q, active, page):
        matching_chats = None
        if q != "" and active == "any":
            matching_chats = Chat.query.join(RegularUser).filter(
                db.or_(RegularUser.username.ilike(f'%{q}%'), Chat.id.ilike(f'%{q}%')), Chat.done == is_active)
        elif active != "any":
            is_active = True if active == "true" else False
            matching_chats = Chat.query.filter_by(active=is_active)
        else:
            matching_chats = Chat.query
        return matching_chats.paginate(page=page, per_page=15)

    def search_users(self, q, active, page):
        matching_users = None
        if q != "" and active == "any":
            matching_users = User.query.join(RegularUser).filter(
                db.or_(RegularUser.username.ilike(f'%{q}%'), User.email.ilike(f'%{q}%'), User.id.ilike(f'%{q}%'))
            )
        elif q != "any":
            is_active = True if active == "true" else False
            matching_users = User.query.join(RegularUser).filter(
                db.or_(RegularUser.username.ilike(f'%{q}%'), User.email.ilike(f'%{q}%'), User.id.ilike(f'%{q}%')),
                User.done = is_active
            )
        elif active != "any":
            is_active = True if active == "true" else False
            matching_users = User.query.filter_by(
                active = is_active
            )
        else:
            matching_users = User.query
        return matching_users.paginate(page=page, per_page=15)

    def __repr__(self):
        return f'<Administration {self.id} : {self.username} - {self.email}>'
