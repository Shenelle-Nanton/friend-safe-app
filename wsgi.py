import click, pytest, sys
from flask import Flask
from flask.cli import with_appcontext, AppGroup
from tabulate import tabulate
from App.database import db, get_migrate
from App.main import create_app
from App.controllers import ( create_user, get_all_users_json, get_all_users )

# This commands file allow you to create convenient CLI commands for testing controllers

app = create_app()
migrate = get_migrate(app)

# This command creates and initializes the database
@app.cli.command("init", help="Creates and initializes the database")
def initialize():
    db.drop_all()
    db.create_all()
    create_user('bob', 'bobpass')
    print('database intialized')

'''
User Commands
'''

# Commands can be organized using groups

# create a group, it would be the first argument of the comand
# eg : flask user <command>
user_cli = AppGroup('user', help='User object commands') 

# Then define the command and any parameters and annotate it with the group (@)
@user_cli.command("create", help="Creates a user")
@click.argument("username", default="rob")
@click.argument("password", default="robpass")
def create_user_command(username, password):
    create_user(username, password)
    print(f'{username} created!')

# this command will be : flask user create bob bobpass

@user_cli.command("list", help="Lists users in the database")
@click.argument("format", default="string")
def list_user_command(format):
    if format == 'string':
        print(get_all_users())
    else:
        print(get_all_users_json())

app.cli.add_command(user_cli) # add the group to the cli

'''
Test Commands
'''

test = AppGroup('test', help='Testing commands') 

@test.command("user", help="Run User tests")
@click.argument("type", default="all")
def user_tests_command(type):
    if type == "unit":
        sys.exit(pytest.main(["-k", "UserUnitTests"]))
    elif type == "int":
        sys.exit(pytest.main(["-k", "UserIntegrationTests"]))
    else:
        sys.exit(pytest.main(["-k", "App"]))
    

app.cli.add_command(test)

@click.argument('chat_id', default=1)
@click.argument('username', default='bob')
@app.cli.command('toggle-chat')
def toggle_chat_command(chat_id, username):
  user = RegularUser.query.filter_by(username=username).first()
  if not user:
    print(f'{username} not found!')
    return
  chat = Chat.query.filter_by(id=chat_id, user_id=user.id).first()
  if not chat:
    print(f'{username} has no chat id {chat_id}')
  chat.toggle()
  print(f'{chat.text} is {"active" if chat.active else "not active"}!')

@click.argument('username', default='bob')
@click.argument('chat_id', default=6)
@click.argument('category', default='groupChat')
@app.cli.command('add-category', help="Adds a category to a Chat")
def add_chat_category_command(username, chat_id, category):
  user = RegularUser.query.filter_by(username=username).first()
  if not user:
    print(f'{username} not found!')
    return
  res = user.add_chat_category(chat_id, category)
  if not res:
    print(f'{username} has no chat id {chat_id}')
    return
  print('Category added!')

@app.cli.command('list-chats')
def list_chats():
  data = []
  for chat in Chat.query.all():
    data.append([ chat.text, chat.active, chat.user.username, chat.cat_list()])
  print (tabulate(data, headers=["Text", "Active", "User", "Categories"]))
