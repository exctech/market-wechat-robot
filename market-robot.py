import asyncio
import re
import time
from datetime import datetime
from typing import List
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from wechaty import Contact, Room, Wechaty, get_logger, Message
log = get_logger('MarketBot')

TOPIC_NAME = "智能播报测试群"
ADMIN_NAME = 'exctech'

async def send_market_info(bot, msg):
    try:
        room = await bot.Room.find(TOPIC_NAME)
        if not room:
            log.warning("未找到行情播报群组")
            return
        await room.say(msg)
    except Exception as e:
        log.exception(e)

async def check_room_join(bot, room, invitee_list, inviter):
    try:
        user_self = bot.user_self()
        if inviter.id != user_self.contact_id:
            await room.say("请联系管理员加入群组")
            scheduler = AsyncIOScheduler()
            for i in invitee_list:
                scheduler.add_job(room.delete, args=[i], seconds=10)
            scheduler.start()
        else:
            await room.say("欢迎加入行情播报群组")
    except Exception as e:
        log.exception(e)

async def manage_market_room(bot):
    time.sleep(3)
    try:
        room = await bot.Room.find(TOPIC_NAME)
        if not room:
            log.warning("未找到行情播报群组")
            return
        log.info("开始监视群组：{}".format(room.room_id))

        def on_join(inviteeList, inviter):
            log.info("群组加入：{}".format(room.room_id))
            check_room_join(bot, room, inviteeList, inviter)

        def on_leave(leaverList, remover):
            log.info("群组离开：{}（by {}）".format(','.join(leaverList), remover or 'unknown'))

        def on_topic(topic, oldTopic, changer):
            log.info("群组修改：旧主题{}，新主题{}（by {}）".format(oldTopic, topic, changer.name()))

        room.on('join', on_join)
        room.on('leave', on_leave)
        room.on('topic', on_topic)
    except Exception as e:
        log.exception(e)

async def put_in_room(contact, room):
    log.info("{}加入{}".format(contact.name, await room.topic()))
    try:
        await room.add(contact)
        scheduler = AsyncIOScheduler()
        scheduler.add_job(lambda x: room.say("欢迎", contact.name))
        scheduler.start()
    except Exception as e:
        log.exception(e)

async def get_out_room(contact, room):
    log.info("{}离开{}".format(contact.name, await room.topic()))
    try:
        await room.say("再见", contact.name)
        await room.delete(contact)
    except Exception as e:
        log.exception(e)

def get_admin_contact(bot):
    return bot.Contact.find(ADMIN_NAME)

async def create_market_room(bot, contact):
    try:
        adminContact = await get_admin_contact(bot)
        if not adminContact:
            log.warning("未设置管理员账号")
            return
        contactList = [contact, adminContact]
        await contact.say("创建行情播报群组")
        room = await bot.Room.create(contactList, TOPIC_NAME)
        await room.say("群组创建成功")
        return room
    except Exception as e:
        log.exception(e)

class MyBot(Wechaty):

    def on_error(self, payload):
        log.info(str(payload))

    def on_logout(self, contact: Contact):
        log.info("{}退出登录".format(contact.name))

    async def on_login(self, contact: Contact):
        msg = "{}已登录".format(contact.name)
        log.info(msg)
        await contact.say(msg)

        msg = "3s后开始设置群组"
        log.info(msg)
        await contact.say(msg)
        await manage_market_room(self)

    async def on_room_join(self, room: Room, invitees: List[Contact],
                           inviter: Contact, date: datetime):
        log.info('Bot' + 'EVENT: room-join - Room "%s" got new member "%s", invited by "%s"' %
                 (await room.topic(), ','.join(map(lambda c: c.name, invitees)), inviter.name))
        topic = await room.topic()
        await room.say("欢迎加入{}！".format(topic), [invitees[0].__str__()])

    async def on_room_leave(self, room: Room, leavers: List[Contact],
                            remover: Contact, date: datetime):
        log.info('Bot' + 'EVENT: room-leave - Room "%s" lost member "%s"' %
                 (await room.topic(), ','.join(map(lambda c: c.name(), leavers))))
        topic = await room.topic()
        name = leavers[0].name if leavers[0] else 'no contact!'
        await room.say("{}离开{}！".format(name, topic))

    async def on_room_topic(self, room: Room, new_topic: str, old_topic: str,
                            changer: Contact, date: datetime):
        try:
            log.info('Bot' + 'EVENT: room-topic - Room "%s" change topic from "%s" to "%s" by member "%s"' %
                     (room, old_topic, new_topic, changer))
            await room.say("群组修改：旧主题{}，新主题{}（by {}）".format(old_topic, new_topic, changer.name()))
        except Exception as e:
            log.exception(e)

    async def on_message(self, msg: Message):
        if msg.age() > 3 * 60:
            log.info('Bot' + 'on(message) skip age("%d") > 3 * 60 seconds: "%s"', msg.age(), msg)
            return
        room = msg.room()
        talker = msg.talker()
        text = msg.text()
        if not talker:
            return
        if msg.is_self():
            return

        if re.search('^market$', text):
            if room:
                if re.search(TOPIC_NAME, await room.topic()):
                    await get_out_room(talker, room)
            else:
                try:
                    marketRoom = await self.Room.find(TOPIC_NAME)
                    if marketRoom:
                        log.info('Bot' + 'onMessage: got marketRoom: "%s"' % await marketRoom.topic())
                        if await marketRoom.has(talker):
                            topic = await marketRoom.topic()
                            log.info('Bot' + 'onMessage: sender has already in marketRoom')
                            await talker.say("已加入群组{}".format(topic))
                        else:
                            log.info('Bot' + 'onMessage: add sender("%s") to marketRoom("%s")' % (talker.name, marketRoom.topic()))
                            await talker.say("邀请加入群组")
                            await put_in_room(talker, marketRoom)
                    else:
                        log.info('Bot' + 'onMessage: marketRoom not found, try to create one')
                        await create_market_room(self, talker)
                        await manage_market_room(self)
                except Exception as e:
                    log.exception(e)

async def main():
    bot = MyBot()
    await bot.start()

if __name__ == '__main__':
    asyncio.run(main())
