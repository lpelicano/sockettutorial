import json 
from channels import Channel
from .settings import (
						NOTIFY_USERS_ON_ENTER_OR_LEAVE_ROOMS, 
						MSG_TYPE_ENTER, 
						MSG_TYPE_LEAVE
						)

from .models import Room
from .utils import get_room_or_error, catch_client_error
from channels.auth import channel_session_user_from_http, channel_session_user
from .exceptions import ClientError


@channel_session_user_from_http
def ws_connect(message):

	# messaage.reply_channel.send() => This accepts the incoming connection 
	message.reply_channel.send({'accept': True})
	
	# Setting value of the rooms key of the channel_session object of the channel to an empty array 
	message.channel_session['rooms'] = []


@channel_session_user
def ws_disconnect(message):

	# Unsubcribe from any connected rooms 

	for room_id in message.channel_session.get("rooms", set()):
		try: 
			room = Room.objects.get(pk=room_id)
			# Removes us from the room's send group. If this doesn't get run, 
			# we'll get removed once our first reply message expires 
			room.websocket_group.discard(message.reply_channel)
		except Room.DoesNotExist: 
			pass

def ws_receive(message): 
	
	# All WebSocket frames have either a text or binary payload; we decode the
    # text part here assuming it's JSON.
    # You could easily build up a basic framework that did this encoding/decoding
    # for you as well as handling common errors.

    payload = json.loads(message['text'])
    payload['reply_channel'] = message.content['reply_channel']
    Channel('chat.receive').send(payload)


# Channel_session_user loads the user out from the channel session and presents
# it as message.user. There's also a http_session_user if you want to do this on
# a low level http handler, or just channel_session if all you want is the 
# message.channel_session object without the auth fetching overhead.

@channel_session_user
@catch_client_error
def chat_join(message):
	# find the room they requested by id and adds them to the send group.
	room  = get_room_or_error(message["room"], message.user)

	# Send a "enter message" to the room if available
	if NOTIFY_USERS_ON_ENTER_OR_LEAVE_ROOMS:
		room.send_message(None, message.user, MSG_TYPE_ENTER)

	room.websocket_group.add(message.reply_channel)
	message.channel_session["rooms"] = list(set(message.channel_session["rooms"]).union([room.id]))
	# send a message back that will prompt them to close the room
	message.reply_channel.send({
		"text": json.dumps({
			"join": str(room.id),
			"title": "Room " + str(room.id),
			}),
	})



@channel_session_user
@catch_client_error
def chat_leave(message):
	# reverse of join - remove the user from the rooms.
	room = get_room_or_error(message["room"], message.user)

	# send a "leave message" to the room if available
	if NOTIFY_USERS_ON_ENTER_OR_LEAVE_ROOMS:
		room.send_message(None, message.user, MSG_TYPE_LEAVE)

	room.websocket_group.discard(message.reply_channel)
	message.channel_session["rooms"] = list(set(message.channel_session["rooms"]).difference([room.id]))
	# send a message back that will prompt them to close the room
	message.reply_channel.send({
		"text": json.dumps({
			"leave": str(room.id),
			}),
	})


@channel_session_user
@catch_client_error
def chat_send(message):

	if int(message["room"]) not in message.channel_session['rooms']:
		raise ClientError("ROOM_ACCESS_DENIED")

	room = get_room_or_error(message["room"], message.user)
	room.send_message(message['message'], message.user)





