from channels import include 


channel_routing = [

	include('chat.routing.websocket_routing', path=r'^/chat/stream'),

	# Custom handler for message sending (see Room.send_message).
	# Can't go in the include above as it does not have a path attribute to match on 
	include('chat.routing.custom_routing'),

]

