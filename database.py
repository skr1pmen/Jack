import sqlite3


class Database:
    def __init__(self, db_file):
        self.connection = sqlite3.connect(db_file)
        self.cursor = self.connection.cursor()

    def chat_exists(self, chat_id):
        with self.connection:
            result = self.cursor.execute("SELECT * FROM `users` WHERE `chat_id` = ?", (chat_id,)).fetchmany(1)
            return bool(len(result))

    def add_chat(self, chat_id, first_name, prem, avatars):
        with self.connection:
            return self.cursor.execute("INSERT INTO `users` (`chat_id`, `first_name`, `prem`, `avatar`) VALUES (?,?,?,?)", (chat_id, first_name, prem, avatars,))

    def group_exists(self, chat_id):
        with self.connection:
            return self.cursor.execute("SELECT `group` FROM `users` WHERE `chat_id` = ?", (chat_id, )).fetchone()[0]

    def add_group(self, chat_id, group):
        with self.connection:
            return self.cursor.execute("UPDATE `users` SET `group` = ? WHERE `chat_id` = ?", (group, chat_id,))

    def len_users_group(self, group):
        return len(self.cursor.execute("SELECT `chat_id` FROM `users` WHERE `group` = ?", (group,)).fetchall())

    def get_chats(self, group, i):
        with self.connection:
            return self.cursor.execute("SELECT `chat_id` FROM `users` WHERE `group` = ?", (group,)).fetchall()[i]

    def new_schedule(self, schedule, group):
        with self.connection:
            return self.cursor.execute("UPDATE `schedules` SET `new_schedule` = ? WHERE `groups` = ?", (schedule, group, ))

    def record_old_schedule(self, group):
        with self.connection:
            schedule = self.cursor.execute("SELECT `new_schedule` FROM `schedules` WHERE `groups` = ?", (group, )).fetchone()[0]
            self.cursor.execute("UPDATE `schedules` SET `old_schedule` = ? WHERE `groups` = ?", (schedule, group, ))

    def schedule(self, group):
        with self.connection:
            new_schedule = self.cursor.execute("SELECT `new_schedule` FROM `schedules` WHERE `groups` = ?", (group, )).fetchone()[0]
            old_schedule = self.cursor.execute("SELECT `old_schedule` FROM `schedules` WHERE `groups` = ?", (group, )).fetchone()[0]

        if new_schedule == old_schedule:
            return False
        else:
            return True

    def schedule_print(self, group):
        with self.connection:
            return self.cursor.execute("SELECT `new_schedule` FROM `schedules` WHERE `groups` = ?", (group, )).fetchone()[0]

    def get_group(self, chat_id):
        with self.connection:
            return  self.cursor.execute("SELECT `group` FROM `users` WHERE `chat_id` = ?", (chat_id, )).fetchone()[0]

    def all_chats(self):
        with self.connection:
            return self.cursor.execute("SELECT `chat_id`, `first_name` FROM `users`")

    def edit_group(self, chat_id):
        with self.connection:
            return self.cursor.execute("UPDATE `users` SET 'group' = 0 WHERE `chat_id` = ?", (chat_id,))

    def get_mailing(self):
        with self.connection:
            return self.cursor.execute("SELECT `mailing` FROM `bot_settings`").fetchone()[0]

    def activate_mailing(self):
        with self.connection:
            return self.cursor.execute("UPDATE `bot_settings` SET `mailing` = 1")

    def deactivate_mailing(self):
        with self.connection:
            return self.cursor.execute("UPDATE `bot_settings` SET `mailing` = 0")

    def if_zero_group(self):
        with self.connection:
            user_zero_group = bool(self.cursor.execute("SELECT `chat_id` FROM `users` WHERE `group` = 0").fetchall())
            return user_zero_group

    def amount_zero_group(self):
        with self.connection:
            return len(self.cursor.execute("SELECT `chat_id` FROM `users` WHERE `group` = 0").fetchall())

    def zero_chat_id(self, i):
        with self.connection:
            return self.cursor.execute("SELECT `chat_id` FROM `users` WHERE `group` = 0").fetchall()[i]

    def if_prem(self, group, i):
        with self.connection:
            return self.cursor.execute("SELECT `prem` FROM `users` WHERE `group` = ?", (group, )).fetchall()[i]