﻿# Copyright 2004-2024 Tom Rothamel <pytom@bishoujo.us>
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation files
# (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

default persistent.show_edit_funcs = True
default persistent.run_dev = False
default persistent.windows_console = False
default persistent.lint_options = set()
default persistent.use_web_doc = False

init python:
    from math import ceil

    def scan_translations(piglatin=True):

        languages = renpy.known_languages()

        if not languages:
            return None

        rv = [(i, renpy.translate_string("{#language name and font}", i)) for i in languages ]
        rv.sort(key=lambda a : renpy.filter_text_tags(a[1], allow=[]).lower())

        rv.insert(0, (None, "English"))

        bound = ceil(len(rv)/3.)
        return (rv[:bound], rv[bound:2*bound], rv[2*bound:])

    class RestartAtPreferences(Action):
        def __call__(self):
            renpy.session["launcher_start_label"] = "preferences"
            renpy.utter_restart()

    class EnsureProjectsTxt(Action):
        """
        Ensures the projects.txt file exists before it's opened.
        """

        def __call__(self):
            fn = os.path.join(project.manager.projects_directory, "projects.txt")

            if os.path.exists(fn):
                return

            with open(fn, "w") as f:
                f.write("""\
# This file can be used to add projects not in the projects directory
# by listing the full path to each project, one per line.

""")


default persistent.force_new_tutorial = False
default persistent.sponsor_message = False
default persistent.daily_update_check = True
default persistent.daily_update_check_once = False

# Keep the default update check from triggering until tomorrow.
default persistent.last_update_check = datetime.date.today()

# Should we try to skip the splashscreen?
default persistent.skip_splashscreen = False

# Should we prefer rpu updates?
default persistent.prefer_rpu = True

init python:
    if not persistent.daily_update_check_once:
        persistent.daily_update_check_once = True
        persistent.daily_update_check = True


default preference_tab = "general"
define preference_tabs = (
    ("general", _("General")),
    ("options", _("Options")),
    ("install", _("Install Libraries")),
    ("lint", _("Lint")),
)

screen preferences():

    default translations = scan_translations()

    frame:
        style_group "l"
        style "l_root"
        alt "Preferences"

        window:

            has vbox

            label _("Launcher Preferences")

            add HALF_SPACER

            hbox:

                frame:
                    style "l_indent"
                    xmaximum ONETHIRD
                    xfill True

                    has vbox

                    add SEPARATOR2

                    add HALF_SPACER

                    for i, l in preference_tabs:
                        textbutton l action SetVariable("preference_tab", i) style "l_list"

                if preference_tab == "general":

                    frame:
                        style "l_indent"
                        xmaximum TWOTHIRDS
                        xfill True

                        has vbox

                        add SEPARATOR2


                        frame:
                            style "l_indent"

                            has vbox

                            text _("Projects Directory:")


                            frame style "l_indent":
                                if persistent.projects_directory:
                                    textbutton _("[persistent.projects_directory!q]"):
                                        action Jump("projects_directory_preference")
                                        alt _("Projects directory: [text]")
                                else:
                                    textbutton _("Not Set"):
                                        action Jump("projects_directory_preference")
                                        alt _("Projects directory: [text]")

                        add SPACER

                        add SEPARATOR2

                        frame:
                            style "l_indent"
                            has vbox

                            text _("Language:")

                            add HALF_SPACER

                            hbox:
                                for tran in translations:
                                    vbox:
                                        for tlid, tlname in tran:
                                            textbutton tlname:
                                                xmaximum (TWOTHIRDS//3)
                                                action [Language(tlid), project.SelectTutorial(True)]
                                                style "l_list"

                elif preference_tab == "options":

                    frame:
                        style "l_indent"
                        xmaximum TWOTHIRDS
                        xfill True

                        has vbox

                        frame:
                            style "l_indent"
                            has vbox

                            textbutton _("Include private names") style "l_checkbox" action ToggleField(persistent, "navigate_private")
                            textbutton _("Include library names") style "l_checkbox" action ToggleField(persistent, "navigate_library")
                            textbutton _("Show edit file section") style "l_checkbox" action ToggleField(persistent, "show_edit_funcs") 

                            if interface.local_doc_exists:
                                textbutton _("Prefer the web documentation") style "l_checkbox" action ToggleField(persistent, "use_web_doc")

                            textbutton _("Restore window position") style "l_checkbox" action Preference("restore window position", "toggle")

                            if ability.can_update:
                                textbutton _("Daily check for update") style "l_checkbox" action [ToggleField(persistent, "daily_update_check"), SetField(persistent, "last_update_check", None)] selected persistent.daily_update_check
                                textbutton _("Prefer RPU updates") style "l_checkbox" action ToggleField(persistent, "prefer_rpu")

                elif preference_tab == "install":

                    frame:
                        style "l_indent"
                        xmaximum TWOTHIRDS
                        xfill True

                        has vbox

                        frame:
                            style "l_indent"
                            has vbox

                            text _("Install Libraries:")

                            add HALF_SPACER

                            use install_preferences

                elif preference_tab == "lint":

                    frame:
                        style "l_indent"
                        xmaximum TWOTHIRDS
                        xfill True

                        has vbox

                        frame:
                            style "l_indent"
                            has vbox

                            text _("Lint toggles:")

                            add HALF_SPACER

                            textbutton _("Check for orphan/obsolete translations"):
                                style "l_checkbox"
                                action InvertSelected(ToggleSetMembership(persistent.lint_options, "--no-orphan-tl"))
                            textbutton _("Check parameters shadowing reserved names"):
                                style "l_checkbox"
                                action ToggleSetMembership(persistent.lint_options, "--reserved-parameters")
                            textbutton _("Print block, word, and character counts by speaking character."):
                                style "l_checkbox"
                                action ToggleSetMembership(persistent.lint_options, "--by-character")
                            textbutton _("Unclosed text tags"):
                                style "l_checkbox"
                                action ToggleSetMembership(persistent.lint_options, "--check-unclosed-tags")
                            textbutton _("Show all unreachable blocks and orphaned translations."):
                                style "l_checkbox"
                                action ToggleSetMembership(persistent.lint_options, "--all-problems")


    textbutton _("Return") action Jump("front_page") style "l_left_button"

label clean_tmp:
    python hide:
        installer.processing(_("Cleaning temporary files..."))
        installer._clean("renpy:tmp", 0)
        time.sleep(0.5)

    jump preferences

label projects_directory_preference:
    call choose_projects_directory
    jump preferences


label preferences:
    call screen preferences
    jump preferences


screen choose_language():
    default local_lang = _preferences.language
    default chosen_lang = _preferences.language
    default translations = scan_translations(piglatin=False)

    add BACKGROUND

    vbox:
        xalign .5
        yalign .5

        fixed:
            ysize 0

            text renpy.translate_string(_("{#in language font}Welcome! Please choose a language"), local_lang):
                xalign .5
                yanchor 1.0
                ypos 1.0

                style "l_label_text"

                size 36
                textalign .5
                layout "subtitle"

        add SPACER
        add SPACER

        hbox:
            xalign .5
            for tran in translations:
                vbox:
                    for tlid, tlname in tran:
                        textbutton tlname:
                            xmaximum (TWOTHIRDS//3)
                            action [ SetScreenVariable("chosen_lang", tlid), Language(tlid), project.SelectTutorial(True), Return() ]
                            hovered SetScreenVariable("local_lang", tlid)
                            unhovered SetScreenVariable("local_lang", chosen_lang)
                            style "l_list"
                            text_xalign .5

        add SPACER
        add SPACER

        $ lang_name = renpy.translate_string("{#language name and font}", local_lang)

        fixed:
            ysize 0

            textbutton renpy.translate_string(_("{#in language font}Start using Ren'Py in [lang_name]"), local_lang):
                xalign .5
                action [Language(chosen_lang), project.SelectTutorial(True), Return()]
                style "l_default"
                text_style "l_default"

                text_size 30
                text_textalign .5
                text_layout "subtitle"


label choose_language:
    call screen choose_language
    return


translate None strings:
    # game/new_project.rpy:77
    old "{#language name and font}"
    new "English"
