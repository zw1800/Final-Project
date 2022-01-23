# Werewolf Game

Background:
This is our final project for Introduction to Computer Science at NYU Shanghai. We were inspired by the message-driven feature of Werewolf Game in reality and we aimed to build a virtual version of the game based on a chat system.

# How to Play
Multi-player Game: Require a chat group of 5 members

Three Roles: Villiger(3), Werewolf(1) and Seer(1)

Each “Day”:

Step 1: Begin conversation to find out the werewolf

Step 2: All players vote for the potential werewolf

Step 3: Werewolf hunts a player

Step 4: Seer can check a player’s identity, go back to Step 1

The game runs on the terminal. No interface is available at the moment.

# Game Design
The whole game is operated based on player’s conversation. There are three components that are essential to the project: chat_server.py, client_state_machine.py and Game.py	

Chat_server.py: Processing the messages from the players and push the game forward, or terminate the game.

Client_state_machine.py: This part receives commands or peer messages from the server and instructs the player to input information needed. Then, this state machine will send players’ messages to the server.

Game.py: Contains a new class: “Game” where a series of specific functions required for the game are defined.



# Compromises and Shortcomings
Hot Seat game -> multiplayer game

Allowing more players

Adding quit option at any stage of the game

Game Interface

# Last but not least...

With great thanks to Professor Xia, who guided us through the implementation of this project.

# Code Citation
