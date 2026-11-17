def setup_all_commands(app):
    from commands.basic_commands import setup_basic_commands
    from commands.enemy_commands import setup_enemy_commands
    from commands.spam_commands import setup_spam_commands
    from commands.autospam_commands import setup_autospam_commands
    from commands.mute_ban_commands import setup_mute_commands
    from commands.reaction_time_commands import setup_reaction_commands, setup_time_commands
    from commands.save_commands import setup_save_commands
    from commands.id_commands import setup_id_commands

    setup_basic_commands(app)
    setup_enemy_commands(app)
    setup_spam_commands(app)
    setup_autospam_commands(app)
    setup_mute_commands(app)
    setup_reaction_commands(app)
    setup_time_commands(app)
    setup_save_commands(app)
    setup_id_commands(app)


__all__ = ["setup_all_commands"]
