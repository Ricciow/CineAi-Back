# Estrutura de um projeto:
# {
#   "_id": "project_id_123",
#   "titulo": "Projeto de IA - Roteiro de Filme",
#   "owner": "user_id_owner",
  
#   "chats": ["chat_id_A", "chat_id_B"],
#   "imagens": ["img_id_C"],
#   "videos": [],
  
#   "accessControl": [
#     {
#       "userId": "user_id_abc",
#       "permissions": {
#         "chats": "edit",   // Pode ler e editar chats
#         "images": "read",  // Pode apenas ler imagens
#         "videos": "none"   // Sem acesso a vídeos
#       }
#     },
#     {
#       "userId": "user_id_xyz",
#       "permissions": {
#         "chats": "read",
#         "images": "read",
#         "videos": "read"
#       }
#     }
#   ]
# }