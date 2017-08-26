from channels import route 
from .consumers import ws_connect, ws_receive, ws_disconnect, chat_join, chat_leave, chat_send

# There's no path matching on these routes, we just rely on the matching from the top level match. 

websocket_routing = [

	route('websocket.connect', ws_connect),
	route('websocket.receive', ws_receive),
	route('websocket.disconnect', ws_disconnect),

]


# Custom routing 

# 

custom_routing = [

	route('chat.receive', chat_join, command='^join$'),
	route('chat.receive', chat_leave, command='^leave$'),
	route('chat.receive', chat_send, command='^send$'),

]

