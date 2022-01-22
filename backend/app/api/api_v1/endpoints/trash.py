""" 
If everything works, delete this file
"""

# @router.post("/{name}/key")
# async def create_msg_key(
#     name: str, keyData: MsgKeysCreate, session: Optional[str] = Cookie(None)
# ):
#     if session:
#         hashed_name = parser.parse_link_hash(name)
#         room = database.get_room_by_name(hashed_name)
#         encoded_data = jsonable_encoder(keyData)
#         user = database.get_user_by_name(
#             decoder.decode_session(session)["username"], room.id
#         )
#         if (
#             decoder.verify_session(hashed_name, room.password, session, True)
#             and user.status
#         ):
#             database.create_msg_key(
#                 room.id, encoded_data["destinied_for"], encoded_data["key"]
#             )
#             return JSONResponse(
#                 content={"Status": "Msg created"}, status_code=status.HTTP_200_OK
#             )
#     return JSONResponse(
#         status_code=status.HTTP_302_FOUND,
#         content={"Unauthorized": "Session doesn't exist"},
#         headers={"Location": f"/rooms/{name}/auth", "Connection": "close"},
#     )


# @router.delete("/{name}/key")
# async def delete_msg_key(name: str, session: Optional[str] = Cookie(None)):
#     if session:
#         hashed_name = parser.parse_link_hash(name)
#         room = database.get_room_by_name(hashed_name)
#         decoded_session = decoder.decode_session(session)
#         user = database.get_user_by_name(decoded_session["username"], room.id)
#         if decoder.verify_session(hashed_name, room.password, session) and user.status:
#             data = database.get_msg_key(room.id, decoded_session["username"])
#             key_session = decoder.session_add_key(session, data.key)
#             await database.delete_key(data.id)
#             return JSONResponse(
#                 status_code=status.HTTP_200_OK,
#                 content={"Status": "The encryption key was received"},
#                 headers={
#                     "Set-Cookie": f"session={key_session}",
#                 },
#             )
#     return JSONResponse(
#         status_code=status.HTTP_302_FOUND,
#         content={"Unauthorized": "Session doesn't exist"},
#         headers={"Location": f"/rooms/{name}/auth", "Connection": "close"},
#     )

# DRY
"""
    hashed_name = parser.parse_link_hash(name)
    room = database.get_room_by_name(hashed_name)
    user = database.get_user_by_name(
        decoder.decode_session(session)["username"], room.id
    )
"""


""" Database """

# def get_msg_key(self, room_id: int, destinied_for: str) -> MsgKeys:
#     keyTable = self.get_table("MsgKeys")
#     with self.session as session:
#         key = (
#             session.query(keyTable)
#             .where(
#                 keyTable.room_id == room_id
#                 and keyTable.destinied_for == destinied_for
#             )
#             .first()
#         )
#         if not key:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND, detail="Key not found"
#             )
#         return key


# def create_msg_key(self, room_id: int, destinied_for: str, key: str) -> bool:
#     keyTable = self.get_table("MsgKeys")
#     if not self.check_msg_key(destinied_for):
#         with self.session as session:
#             note = keyTable(room_id=room_id, destinied_for=destinied_for, key=key)
#             session.add(note)
#             session.commit()
#     else:
#         raise HTTPException(
#             status_code=status.HTTP_409_CONFLICT, detail="Key alredy created"
#         )

# def delete_key(self, keyId: int):
#     keyTable = self.get_table("MsgKeys")
#     with self.session as session:
#         key = session.query(keyTable).where(keyTable.id == keyId).one()
#         session.delete(key)
#         session.commit()
