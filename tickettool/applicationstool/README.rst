.. _applicationtool:
==========
ApplicationTool
==========

This is the cog guide for the 'ApplicationTool' cog. This guide contains the collection of commands which you can use in the cog.
Through this guide, ``[p]`` will always represent your prefix. Replace ``[p]`` with your own prefix when you use these commands in Discord.

.. note::

    Ensure that you are up to date by running ``[p]cog update applicationtool``.
    If there is something missing, or something that needs improving in this documentation, feel free to create an issue `here <https://github.com/AAA3A-AAA3A/AAA3A-cogs/issues>`_.
    This documentation is auto-generated everytime this cog receives an update.

--------------
About this cog
--------------

A cog to manage an application system!

--------
Commands
--------

Here are all the commands included in this cog (39):

* ``[p]setapplicationtool``
 Configure ApplicationTool for your server.

* ``[p]setapplicationtool adminrole <profile> [role]``
 Users with this role will have full permissions for applications, but will not be able to set up the cog.

* ``[p]setapplicationtool auditlogs <profile> [audit_logs]``
 On all requests to the Discord api regarding the application (channel modification), does the bot send the name and id of the user who requested the action as the reason?

* ``[p]setapplicationtool categoryclose <profile> [category channel]``
 Set the category where the closed applications will be.

* ``[p]setapplicationtool categoryopen <profile> [category channel]``
 Set the category where the opened applications will be.

* ``[p]setapplicationtool closeconfirmation <profile> [close_confirmation]``
 Should the bot ask for confirmation before closing the application (deletion will necessarily have a confirmation)?

* ``[p]setapplicationtool closeonleave <profile> [close_on_leave]``
 If a user leaves the server, will all their open applications be closed?

* ``[p]setapplicationtool createonreact <profile> [create_on_react]``
 Open an application when the reaction 🎟️ is set on any message on the server.

* ``[p]setapplicationtool custommessage <profile> [custom_message]``
 This message will be sent in the application channel when the application is opened.

* ``[p]setapplicationtool deleteonclose <profile> [delete_on_close]``
 Does closing the application directly delete it (with confirmation)?

* ``[p]setapplicationtool dynamicchannelname <profile> [dynamic_channel_name]``
 Set the template that will be used to name the channel when creating an application.

* ``[p]setapplicationtool enable <profile> [enable]``
 Enable the system.

* ``[p]setapplicationtool logschannel <profile> [text channel]``
 Set the channel where the logs will be saved.

* ``[p]setapplicationtool message <panel> [channel] [message] [reason_options]...``
 Send a message with a button to open an application or dropdown with possible reasons.

* ``[p]setapplicationtool modalconfig <profile> [confirmation=False]``
 Set all settings for the cog with a Discord Modal.

* ``[p]setapplicationtool modlog <profile> [modlog]``
 Does the bot create an action in the bot modlog when an application is created?

* ``[p]setapplicationtool nbmax <profile> [nb_max]``
 Sets the maximum number of open applications a user can have on the system at any one time (for the profile only).

* ``[p]setapplicationtool pingrole <profile> [role]``
 This role will be pinged automatically when the application is created, but does not give any additional permissions.

* ``[p]setapplicationtool profileadd <profile>``
 Create a new profile with defaults settings.

* ``[p]setapplicationtool profileclone <old_profile> <profile>``
 Clone an existing profile with his settings.

* ``[p]setapplicationtool profileremove <profile> [confirmation=False]``
 Remove an existing profile.

* ``[p]setapplicationtool profilerename <old_profile> <profile>``
 Clone an existing profile with his settings.

* ``[p]setapplicationtool profileslist``
 List the existing profiles.

* ``[p]setapplicationtool showsettings <profile> [with_dev=False]``
 Show all settings for the cog with defaults and values.

* ``[p]setapplicationtool supportrole <profile> [role]``
 Users with this role will be able to participate and claim the application.

* ``[p]setapplicationtool usercanclose <profile> [user_can_close]``
 Can the author of the application, if he/she does not have a role set up for the system, close the application himself?

* ``[p]setapplicationtool viewrole <profile> [role]``
 Users with this role will only be able to read messages from the application, but not send them.

* ``[p]application``
 Commands for using the application system.

* ``[p]application add [members]... [reason=No reason provided.]``
 Add a member to an existing application.

* ``[p]application claim [member=None] [reason=No reason provided.]``
 Claim an existing application.

* ``[p]application close [confirmation=None] [reason=No reason provided.]``
 Close an existing application.

* ``[p]application create [panel=main] [reason=No reason provided.]``
 Open an application.

* ``[p]application delete [confirmation=False] [reason=No reason provided.]``
 Delete an existing application.

* ``[p]application export``
 Export all the messages of an existing application in html format.

* ``[p]application open [reason=No reason provided.]``
 Open an existing application.

* ``[p]application owner <new_owner> [reason=No reason provided.]``
 Change the owner of an existing application.

* ``[p]application remove [members]... [reason=No reason provided.]``
 Remove a member to an existing application.

* ``[p]application rename <new_name> [reason=No reason provided.]``
 Rename an existing application.

* ``[p]application unclaim [reason=No reason provided.]``
 Unclaim an existing application.

------------
Installation
------------

If you haven't added my repo before, lets add it first. We'll call it
"AAA3A-cogs" here.

.. code-block:: ini

    [p]repo add AAA3A-cogs https://github.com/AAA3A-AAA3A/AAA3A-cogs

Now, we can install ApplicationTool.

.. code-block:: ini

    [p]cog install AAA3A-cogs applicationtool

Once it's installed, it is not loaded by default. Load it by running the following command:

.. code-block:: ini

    [p]load applicationtool

---------------
Further Support
---------------

Check out my docs `here <https://aaa3a-cogs.readthedocs.io/en/latest/>`_.
Mention me in the #support_other-cogs in the `cog support server <https://discord.gg/GET4DVk>`_ if you need any help.
Additionally, feel free to open an issue or pull request to this repo.

------
Credit
------

Thanks to Kreusada for the Python code to automatically generate this documentation!
