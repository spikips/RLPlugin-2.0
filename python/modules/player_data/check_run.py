from modules.widgets.widget import click_widget


def click_run(enable=True):
    if enable:
        run = click_widget('10485790', sprite_id=1065)
        if run:
            print('run enabled')
        else:
            print('run already enabled')
    else:
        walk = click_widget('10485790', sprite_id=1064)
        if walk:
            print('walk enabled')
        else:
            print('walk already enabled')



# click_run(enable=False)
