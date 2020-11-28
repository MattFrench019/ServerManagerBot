
class Channels:
    rules = 769233668027580488
    select = 769233721281871873
    pending = 769236016669392957
    admissions = 769468795881652224
    log = 781916293821497375
    game_select = 781923452243673118
    game_def = 781923712362217472
    control = 782167175158562816


class Emojis:
    rules_tick = "acceptrules"
    y10 = "10"
    y13 = "13"
    wing = "winghouse"
    user_tick = "acceptuser"
    user_cross = "denyuser"
    user_ban = "banuser"


class Roles:
    on_join = 769235436496486440
    on_rules_click_add = 769234280332918806
    on_rules_click_rem = 769235436496486440
    on_select_click_add = 769234350968930385
    on_select_click_rem = 769234280332918806
    member = 769460090452443136
    y13 = 719903094640738346
    y10 = 719901525807333397
    wing = 769281855455232030
    game_label = 712951344159260672


server = 694952036772479001
groups_len = 3
reset_cmd = "$reset"
channels = Channels()
emojis = Emojis()
roles = Roles()
emojis_to_roles = {
    emojis.y10: roles.y10,
    emojis.y13: roles.y13,
    emojis.wing: roles.wing
}
emojis_to_group = {
    emojis.y10: "Year 10",
    emojis.y13: "Year 13",
    emojis.wing: "Wing House"
}
group_to_emoji = {emojis_to_group[k]: k for k in emojis_to_group}
