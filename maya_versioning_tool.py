import os
import glob
import re
from functools import partial
import maya.cmds as mc


class MayaVersioningTool(object):

    def __init__(self, src='C:/Users/raju/PycharmProjects/Episodes'):
        self.src = src
        self.all_eps = {}
        self.current_file_path = None
        self.current_file = None
        self.selected_file = None
        self.maya_file_types = {".ma": "mayaAscii", '.mb': 'mayaBinary'}

    def all_ep_seq_shot(self):
        for ep in glob.glob("%s/*" % self.src):
            if os.path.isdir(ep):
                ep_dir = os.path.split(ep)[-1]
                self.all_eps[ep_dir] = {}
                for seq in glob.glob("%s/*" % ep):
                    seq_dir = os.path.split(seq)[-1]
                    self.all_eps[ep_dir][seq_dir] = os.listdir(seq)

    def delete_menu_items(self, target_ui_element='', *args):
        old_menu_items = mc.optionMenu(target_ui_element, q=True, ils=True)
        old_menu_items = old_menu_items if old_menu_items else []
        for omi in old_menu_items:
            mc.deleteUI(omi)

    def ep_changed(self, item, target_ui_element='', *args, **kwargs):

        self.all_ep_seq_shot()
        mc.textScrollList(self.files, e=True, ra=True)
        self.delete_menu_items(target_ui_element=self.seqs)
        self.delete_menu_items(target_ui_element=self.shots)

        mc.optionMenu(target_ui_element, w=100, h=30, e=True,
                      cc=partial(self.seq_changed, target_ui_element=self.shots))
        seq_dirs = self.all_eps[item].keys()
        mc.menuItem(l='--', p=target_ui_element)
        seq_dirs.sort()
        for seq in seq_dirs:
            mc.menuItem(l=seq, p=target_ui_element)
        self.c_ep = item

    def seq_changed(self, item, target_ui_element='', *args, **kwargs):

        self.all_ep_seq_shot()
        self.delete_menu_items(target_ui_element=self.shots)
        mc.textScrollList(self.files, e=True, ra=True)
        mc.optionMenu(target_ui_element, w=100, h=30, e=True, cc=partial(self.shot_changed))
        cep = mc.optionMenu(self.eps, q=True, value=True)
        shot_dirs = self.all_eps[cep][item]

        shot_dirs.sort()
        mc.menuItem(l='--', p=target_ui_element)
        for seq in shot_dirs:
            mc.menuItem(l=seq, p=target_ui_element)
        self.c_seq = item

    def shot_changed(self, item, *args):
        self.c_shot = item
        print ('shot changed %s' % item)

        self.current_file_path = "{0}/{1}/{2}/{3}".format(self.src, self.c_ep, self.c_seq, self.c_shot)
        mc.textScrollList(self.files, e=True, ra=True)
        for f in glob.glob("{0}/*.ma".format(self.current_file_path)):
            f_name = os.path.basename(f)
            print mc.textScrollList(self.files, e=True, a=f_name)
        pass

    def open_file(self, *args):

        if self.selected_file:
            self.current_file = "{0}/{1}".format(self.current_file_path, self.selected_file)
            mc.file(self.current_file, f=True, o=True)
        else:
            mc.confirmDialog(m="no file selected", b=['Ok'])

    def set_project(self, *args):
        if self.current_file_path:
            mc.workspace(self.current_file_path, o=True)
            mc.workspace(dir=self.current_file_path)
            mc.workspace(s=True)
            mc.textField(self.ws_path, e=True, tx=mc.workspace(q=True, dir=True), ed=False, h=30)
        else:
            print ("not path set")

    def make_version(self, *args):

        if self.current_file:
            c_file = mc.file(loc=True, q=True)
            path_splits = os.path.split(c_file)
            cext = os.path.splitext(path_splits[-1])
            name_splits = cext[0].split("_")
            res_grp = re.search(r"(\w)(\d+)", name_splits[-1])

            if res_grp and len(res_grp.groups()) == 2:
                c_version_prefix = res_grp.group(1)
                c_version_str = res_grp.group(2)
                c_version_num = int(c_version_str)
                next_ver_num = c_version_num + 1
                next_ver_str = "{0}{1:02}".format(c_version_prefix, next_ver_num)
                name_splits[-1] = next_ver_str
                new_name = "_".join(name_splits)
                res_name = "{0}/{1}{2}".format(path_splits[0], new_name, cext[-1])
                self.save_file(file_name=res_name)
        else:
            choice = mc.confirmDialog(m="No file opened from the versioning tool ", b=['Ok'])

    def save_file(self, file_name="", *args):

        cext = os.path.splitext(file_name)
        if not os.path.exists(file_name):
            mc.file(rename=file_name)
            mc.file(save=True, type=self.maya_file_types[cext[-1]])
            self.shot_changed(self.c_shot)
        else:
            choice = mc.confirmDialog(m="{0} already exists, Do you want to Overwrite?".format(file_name),
                                      b=['Cancel', "Yes", "Save Current"])
            print choice
            if choice == "Yes":
                mc.file(rename=file_name)
                mc.file(save=True, type=self.maya_file_types[cext[-1]])
                self.shot_changed(self.c_shot)
            elif choice == "Save Current":
                mc.file(save=True, type=self.maya_file_types[cext[-1]], f=True)
            else:
                mc.warning("No version created,Skipped..........")

    def file_select(self, *args):
        self.selected_file = mc.textScrollList(self.files, q=True, si=True)[0]
        print self.selected_file

    def show(self, *args):
        self.all_ep_seq_shot()
        if mc.window("MayaVersioningTool", ex=True, q=True):
            mc.deleteUI("MayaVersioningTool")
        if mc.windowPref("MayaVersioningTool", ex=True, q=True):
            mc.windowPref("MayaVersioningTool", r=True)
        mc.window("MayaVersioningTool", wh=(370, 600), s=False)
        form_lay = mc.formLayout(numberOfDivisions=300)
        self.eps = mc.optionMenu(w=100, h=30, )
        mc.menuItem(l="--")
        for ep in self.all_eps.keys():
            mc.menuItem(l=ep)
        proj_label = mc.text(l="Project Root", h=30, w=80)
        prj_path = mc.textField(tx=self.src, ed=False, h=30)

        ws_label = mc.text(l="Workspace Path", h=30, w=80)
        self.ws_path = mc.textField(tx=mc.workspace(q=True, dir=True), ed=False, h=30)

        self.seqs = mc.optionMenu(w=150, h=30, p=form_lay)
        self.shots = mc.optionMenu(w=100, h=30, p=form_lay)
        self.files = mc.textScrollList(sc=self.file_select, p=form_lay)
        self.open_btn = mc.button(l="Open", c=self.open_file, p=form_lay)
        self.project_btn = mc.button(l="Set Project", c=self.set_project, p=form_lay)
        self.save_btn = mc.button(l="Save", c="mc.file(s=True,f=True)", p=form_lay)
        self.ver_btn = mc.button(l="Version Up", c=self.make_version, p=form_lay)
        mc.optionMenu(self.eps, e=True, cc=partial(self.ep_changed, target_ui_element=self.seqs), p=form_lay)
        mc.optionMenu(self.seqs, e=True, cc=partial(self.seq_changed, target_ui_element=self.shots), p=form_lay)

        mc.formLayout(form_lay, e=True,
                      af=[(ws_label, 'left', 10),
                          (self.ws_path, 'right', 10), (self.ws_path, 'top', 50), (ws_label, 'top', 50),
                          (proj_label, 'left', 10),
                          (prj_path, 'right', 10), (prj_path, 'top', 20), (proj_label, 'top', 20),
                          (self.eps, 'top', 80), (self.shots, 'top', 80), (self.seqs, 'top', 80),
                          (self.eps, 'left', 10), (self.shots, 'right', 10), (self.files, 'right', 100),
                          (self.files, 'left', 10), (self.files, 'bottom', 10), (self.open_btn, 'left', 10),
                          (self.open_btn, 'top', 30), (self.project_btn, 'right', 10), (self.open_btn, 'right', 10),
                          (self.ver_btn, 'right', 10), (self.save_btn, 'right', 10)
                          ],
                      ac=[
                          (self.seqs, 'left', 10, self.eps), (self.shots, 'left', 10, self.seqs),
                          (self.files, 'top', 10, self.eps), (self.open_btn, 'left', 10, self.files),
                          (self.open_btn, 'top', 10, self.shots), (self.project_btn, 'top', 10, self.ver_btn),
                          (self.project_btn, 'left', 10, self.files), (self.ver_btn, 'top', 10, self.save_btn),
                          (self.ver_btn, 'left', 10, self.files), (prj_path, 'left', 10, proj_label),
                          (self.ws_path, 'left', 10, ws_label), (self.save_btn, 'top', 10, self.open_btn),
                          (self.save_btn, 'left', 10, self.files)
                      ],
                      )
        mc.showWindow("MayaVersioningTool")


if __name__ == "__main__":
    MayaVersioningTool(src='C:/Users/raju/PycharmProjects/Episodes').show()
