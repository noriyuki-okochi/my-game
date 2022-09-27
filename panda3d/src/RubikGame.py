import sys
import time
import math
import random
#from turtle import color, position
from panda3d.core import WindowProperties
from panda3d.core import TextNode
from panda3d.core import DirectionalLight
from panda3d.core import LVector3

from direct.showbase.ShowBase import ShowBase
from direct.showbase.ShowBaseGlobal import globalClock

from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectGui import *

from rubikcube.rubikcube import RubikCube
from mycli.mycli import MyCli
import pickle
from mysqlite3.mysqlite3 import MyDb

class RubikGame(ShowBase):
    PLAY_MODE = 0
    SET_MODE = 1
    MENU_MODE = 2
    DB_PATH = "./db/Rubik-cube.db"
    def __init__(self):
        #ShowBase.__init__(self)
        super().__init__(self)
        # defalut settinge value
        #    ['cmdfile-name', 
        #     {0:don't auto-reg.|1:aoto-reg.}
        #     {0:don't auto-search|1:aoto-search}
        #    ]
        self.setting = ["./dat/cmdfile", '1', '1']
        # serialized-file
        self.settingfile = "./reg/setting.reg"
        # log-file
        self.logfile = f"./log/logfile_{time.strftime('%Y%m%d')}"
        # command-file
        self.cmdfile = f"{self.setting[1]}" 
        self.cmdfileSetting = False
        self.read_fd = None
        self.read_count = 0
        self.autoStart = False
        self.preDt = 0
        self.cmdKeyinSetting = False
        self.pattern_viewing = False
        # 
        self.selected_face = None
        self.cmdBuffer = [] # display buffer for primitive cmd. 
        self.subBuffer = [] # work buffer for sequence cmd.
        self.undoPos = None
        self.copyBuffer = [] # copy/past buffer. 
        # 
        self.restartFlag = False
        #
        self.upsideDownFlag = False
        # set SWB-cube's left-bottom  to ogirin(0, 0, 0)
        self.cube_x = 0
        self.cube_y = 0
        self.cube_z = 0
        self.cube_u = 1
        # set initial H(headding),P(pitch),R(roll) of all cubes
        self.cube_h = 0
        self.cube_p = 0
        self.cube_r = 0
        #
        # define Center-Cubes
        #
        #1 cube_s
        self.cube_s = RubikCube(self, '1', "models/misc/RubikCube")
        #2 cube_n
        self.cube_n = RubikCube(self, '1', "models/misc/RubikCube")
        #3 cube_e
        self.cube_e = RubikCube(self, '1', "models/misc/RubikCube")
        #4 cube_w
        self.cube_w = RubikCube(self, '1', "models/misc/RubikCube")
        #5 cube_t
        self.cube_t = RubikCube(self, '1', "models/misc/RubikCube")
        #6 cube_b
        self.cube_b = RubikCube(self, '1', "models/misc/RubikCube")
        #
        # define Corner-Cubes
        #
        #1 cube_bsw
        self.cube_bsw = RubikCube(self, '3', "./models/misc/RubikCube")
        #2 cube_bse
        self.cube_bse = RubikCube(self, '3', "./models/misc/RubikCube")
        #3 cube_ben
        self.cube_ben = RubikCube(self, '3', "./models/misc/RubikCube")
        #4 cube_bwn
        self.cube_bwn = RubikCube(self, '3', "./models/misc/RubikCube")
        #5 cube_tsw
        self.cube_tsw = RubikCube(self, '3', "./models/misc/RubikCube")
        #6 cube_tse
        self.cube_tse = RubikCube(self, '3', "./models/misc/RubikCube")
        #7 cube_ten
        self.cube_ten = RubikCube(self, '3', "./models/misc/RubikCube")
        #8 cube_twn
        self.cube_twn = RubikCube(self, '3', "./models/misc/RubikCube")
        #
        # define Edge-Cubes
        # 
        #1 cube_sw
        self.cube_sw = RubikCube(self, '2', "./models/misc/RubikCube")
        #2 cube_bs
        self.cube_bs = RubikCube(self, '2', "./models/misc/RubikCube")
        #3 cube_se
        self.cube_se = RubikCube(self, '2', "./models/misc/RubikCube")
        #4 cube-ts
        self.cube_ts = RubikCube(self, '2', "./models/misc/RubikCube")
        #5 cube_nw
        self.cube_nw = RubikCube(self, '2', "./models/misc/RubikCube")
        #6 cube_bn
        self.cube_bn = RubikCube(self, '2', "./models/misc/RubikCube")
        #7 cube_en
        self.cube_ne = RubikCube(self, '2', "./models/misc/RubikCube")
        #8 cube-tn
        self.cube_tn = RubikCube(self, '2', "./models/misc/RubikCube")
        #9 cube_bw
        self.cube_bw = RubikCube(self, '2', "./models/misc/RubikCube")
        #10 cube_be
        self.cube_be = RubikCube(self, '2', "./models/misc/RubikCube")
        #11 cube-te
        self.cube_te = RubikCube(self, '2', "./models/misc/RubikCube")
        #12 cube-tw
        self.cube_tw = RubikCube(self, '2', "./models/misc/RubikCube")
        #
        # center cubes list
        self.cube1 = [self.cube_s, self.cube_n, self.cube_e, self.cube_w, self.cube_t, self.cube_b]
        # edge cubes list
        self.cube2 = [self.cube_ts, self.cube_tn, self.cube_te, self.cube_tw, 
                      self.cube_bs, self.cube_bn, self.cube_be, self.cube_bw,
                      self.cube_sw, self.cube_se, self.cube_nw, self.cube_ne,]
        # corner cubes list
        self.cube3 = [self.cube_tsw, self.cube_tse, self.cube_ten, self.cube_twn, 
                      self.cube_bsw, self.cube_bse, self.cube_ben, self.cube_bwn]
        #
        # connect Rubik-cube.db
        #
        self.db = MyDb(RubikGame.DB_PATH)
        #
        # set window properties
        #
        self.win_attr = WindowProperties()
        #
        self.disableMouse()
        #
        dir_light = DirectionalLight("directionalLight")
        dir_light.setDirection(LVector3(0, 0, -1))
        #dir_light.setColor((0.375, 0.375, 0.375, 1))
        #dir_light.setSpecularColor((1, 1, 1, 1))
        light = self.render.attachNewNode(dir_light)
        #
        font = self.loader.loadFont("./fonts/msgothic.ttc")      
        #  
        #
        # CLI command input-line
        #
        self.cli = MyCli(self, font)
        #
        # ope. command display(history)-line
        #
        self.cmdline = OnscreenText(text="操作ログ：",
                   parent=self.a2dTopLeft, align=TextNode.ALeft,
                   fg=(1, 1, 1, 1), pos=(0.1, -1.90), 
                   scale=0.06, font=font,
                   shadow=(0, 0, 0, 0.5))
        #
        # cube's face rotate-ope. command guidance
        # 
        guid_text =" south/north/east/west/top/bottom\n"\
                   " Green/Blue/Orange/Red/Yellow/White\n\n"\
                   " +:Right -:Left\n"\
                   " y:Y-ex  z:Z-ex v:Inter {<|>}:Around\n\n"\
                   " u:Undo last cmd.\n"\
                   " ctrl+z:Cancel un-confirmed cmd.\n"\
                   " enter:Confirm(save cmd. and clear)\n"\
                   " escape:Suspend current sequence."    
        self.guidance1 = OnscreenText(text = guid_text,
                   parent=self.a2dTopLeft, align=TextNode.ALeft,
                   fg=(1, 1, 1, 1), pos=(1.5, -0.1), 
                   scale=0.06, font=font,
                   shadow=(0, 0, 0, 0.5))
        #
        # cammera's position move-ope. command guidance
        # 
        guid_text = " →←↑↓: Move camera\n"\
                    " home    : Home position\n"\
                    " o:Opposit  pg-up:UpSideDown"
        self.guidance2 = OnscreenText(text = guid_text,
                   parent=self.a2dTopLeft, align=TextNode.ALeft,
                   fg=(1, 1, 1, 1), pos=(0.54, -0.1), 
                   scale=0.06, font=font,
                   shadow=(0, 0, 0, 0.5))
        #
        # game control-ope. command guidance
        # 
        guid_text = " ctrl+r:Recover from reg.\n"\
                    " ctrl+s:Start game\n"\
                    " ctrl+f:Read cmd. from file\n"\
                    " ctrl+i:Input cmd. by key\n"\
                    " ctrl+c/p:Copy/Past cmd.\n"\
                    " ctrl+q/e:Quit/Exit(with reg.)\n "
        self.guidance3 = OnscreenText(text = guid_text,
                   parent=self.a2dTopLeft, align=TextNode.ALeft,
                   fg=(1, 1, 1, 1), pos=(0.54, -0.31), 
                   scale=0.06, font=font,
                   shadow=(0, 0, 0, 0.5))
        #
        # setting menu or CLI command guidance
        # 
        self.menu = OnscreenText(text = '',
                   parent=self.a2dTopLeft, align=TextNode.ALeft,
                   fg=(0, 1, 1, 1), pos=(0.05, -0.65), 
                   scale=0.06, font=font,
                   shadow=(0, 0, 0, 0.5))
        #
        # Radio-Button list( Game-mode selection)
        #
        self.ope_mode = [0]
        buttons = [
            DirectRadioButton(text='playing mode', command = self.on_playing, 
                              variable = self.ope_mode, value = [RubikGame.PLAY_MODE], 
                              scale = 0.070, pos = (0.3, 0, -0.1), 
                              parent = self.a2dTopLeft, boxPlacement = 'left'),
            DirectRadioButton(text='setting mode', command = self.on_setting,
                              variable = self.ope_mode, value = [RubikGame.SET_MODE], 
                              scale = 0.070, pos = (0.3, 0, -0.2), 
                              parent = self.a2dTopLeft, boxPlacement = 'left')
        ]
        for button in buttons:
            button.setOthers(buttons)
        #  
        # key event definition
        #
        '''
        "escape", "f"+"1-12" (e.g. "f1","f2",..."f12"), "print_screen" "scroll_lock"
	    "backspace", "insert", "home", "page_up", "num_lock"
	    "tab",  "delete", "end", "page_down"
	    "caps_lock", "enter", "arrow_left", "arrow_up", "arrow_down", "arrow_right"
	    "shift", "lshift", "rshift",
	    "control", "alt", "lcontrol", "lalt", "space", "ralt", "rcontrol"
        '''
        # move the camera
        self.accept("arrow_up-repeat", self.up_key)
        self.accept("arrow_down-repeat", self.down_key)
        self.accept("arrow_right-repeat", self.right_key)
        self.accept("arrow_left-repeat", self.left_key)
        # reset the camera's position
        self.accept("home", self.reset_camera)
        self.accept("o", self.opposit_camera)
        # turn the rubic-cube upside down
        self.accept("page_up", self.upside_down)
        # set all cube to initial position( restart game)
        self.accept("control-s", self.re_start)

        # select a face(t/b/s/n/e/w) relatively
        self.accept("t", self.top_face)
        self.accept("b", self.bottom_face)
        self.accept("s", self.south_face)
        self.accept("n", self.north_face)
        self.accept("e", self.east_face)
        self.accept("w", self.west_face)
        # select a face(Yellow/Wite/Green/Blue/Orange/Red) absolutly
        self.accept("shift-y", self.yellow_face)
        self.accept("shift-w", self.white_face)
        self.accept("shift-g", self.green_face)
        self.accept("shift-b", self.blue_face)
        self.accept("shift-o", self.orange_face)
        self.accept("shift-r", self.red_face)
        # rotate the selected face 
        self.accept(";", self.right_char)
        self.accept("-", self.left_char)
        # suspend current seaquence
        self.accept("escape", self.escape)
        # undo last operation
        self.accept("u", self.undo)
        # save operations in command-line and clear command-line
        self.accept("enter", self.confirm)
        # undo all operations in command-line and clear command-line
        self.accept("control-z", self.cancel)
        # read command-line from cmdfile and execute these comannds
        self.accept("control-f", self.read_file)
        self.accept("control-a", self.auto_start)
        # input commands with key and execute these comannds
        self.accept("control-i", self.input_cmd)
        # copy commands from log to input and execute these comannds
        self.accept("control-c", self.copy_cmd)
        self.accept("control-p", self.past_input)
        # exit from game
        self.accept("control-q", self.quit)
        self.accept("control-e", self.exit)
        # restore cube's attr from reg-file
        self.accept("control-r", self.restore)
        # setting mode
        self.accept("space", self.space_key)
        self.accept("backspace", self.backspace_key)
        self.accept("delete", self.delete_key)
        self.accept("arrow_right", self.cursor_right)
        self.accept("arrow_left", self.cursor_left)
        self.accept("a", self.a_key)
        self.accept("c", self.c_key)
        self.accept("d", self.d_key)
        self.accept("f", self.f_key)
        self.accept("g", self.g_key)
        self.accept("h", self.h_key)
        self.accept("i", self.i_key)        
        self.accept("j", self.j_key)
        self.accept("k", self.k_key)
        self.accept("l", self.l_key)
        self.accept("m", self.m_key)
        self.accept("r", self.r_key)
        self.accept("p", self.p_key)
        self.accept("q", self.q_key)
        self.accept("v", self.v_key)
        self.accept("x", self.x_key)
        self.accept("y", self.y_key)
        self.accept("z", self.z_key)
        self.accept("shift-s", self.upper_s)
        self.accept("shift-e", self.upper_e)
        self.accept("shift-n", self.upper_n)
        self.accept("shift-t", self.upper_t)
        self.accept(".", self.dot_key)
        self.accept(",", self.comma_key)
        self.accept("/", self.slash_key)
        self.accept("shift-5", self.persent_key)
        self.accept("shift-\\", self.under_key)
        self.accept("1", self.num1_key)
        self.accept("2", self.num2_key)
        self.accept("3", self.num3_key)
        self.accept("4", self.num4_key)
        self.accept("5", self.num5_key)
        self.accept("6", self.num6_key)
        self.accept("7", self.num7_key)
        self.accept("8", self.num8_key)
        self.accept("9", self.num9_key)
        self.accept("0", self.num0_key)
        # mouse operation
        self.accept("mouse1", self.mouse1_click)
        #
        # load setting value from reg. file
        #
        try:
            with open(f"{self.settingfile}", 'rb') as fd:
                self.setting = pickle.load(fd)
                self.cmdfile = f"{self.setting[0]}" 
        except:
            print(f"setting-file:{self.settingfile} not exist.")
        print(f"setting:{self.setting}")
        #
        #  set the camera to initial position
        #
        self.reset_camera() 
        #
        # set the initial position of all cubes 
        #
        self.set_initial_cube()
    #
    #  Task to execute rotatinon command  with timer
    #     
    def autoTask(self, task):
        dt = globalClock.getFrameTime()
        if self.autoStart:
            dt = int(dt)
            #self.write_opelog(f"dt:{dt}")
            if dt != self.preDt:
                self.preDt = dt
                if self.readf_next() == None:
                    self.cli.prompt('')
                else:
                    self.cli.prompt('...executing...')
        return task.cont
    #
    # call-back func. on radio-bottom click
    #
    def on_playing(self):
        self.cur_mode = RubikGame.PLAY_MODE
        self.menu.setText('')
        self.cli.clear()
    #    
    def on_setting(self):
        self.cur_mode = RubikGame.SET_MODE
        self.set_help_text()
        self.cli.start()
    #
    # display CLI command guidance
    #
    def set_help_text(self):
        help_text = f"set: dislay setting menu.\n"\
                    f"pt  <r|v|s|g|d> [arg.] :pattern Reg/View/Search/Get/Del.\n"\
                    f"reg <file-name>:reg. cube's pattern.\n"\
                    f"ld  <file-name>:load cube's pattern.\n"\
                    f"lw  <file-name> [<start-end>]:log-file copy.\n"
        self.menu.setText(help_text)
        return
    #
    # display setting menu(refresh by current setting value)
    #
    def set_menu_text(self, reg = False):
        menu_text = f"1.cmd. file name(str) : {self.setting[0]}\n"\
                    f"2.auto reg.[N=0/Y=1]  : {self.setting[1]}\n"\
                    f"3.auto search[N=0/Y=1]: {self.setting[2]}\n"\
                    f"0.quit\n"
        self.menu.setText(menu_text)
        if reg:
            # registory current setting-value
            with open(f"{self.settingfile}", 'wb') as fd:
                pickle.dump(self.setting, fd, pickle.HIGHEST_PROTOCOL)
        return
    #
    # save command-buffer to log-file
    #
    def write_cmdlog(self, cmdbuf):
        fd = open(self.logfile, mode='a+')
        fd.writelines(cmdbuf)
        fd.write('\n')
        fd.close()
        return
    #
    # save operation-log(with top character '#') to log-file
    #
    def write_opelog(self, mesg):
        fd = open(self.logfile, mode='a+')
        fd.write(f"#{mesg}\n")
        fd.close()
    #
    # set initial(complete) position of all cubes 
    #
    def set_initial_cube(self):
        self.upsideDownFlag = False
        # set Centor-Cubes
        #1 cube_s
        self.cube_s.setPos(self.cube_x + self.cube_u, self.cube_y, self.cube_z + self.cube_u)
        self.cube_s.setHpr(self.cube_h, self.cube_p, self.cube_r)
        #2 cube_n
        self.cube_n.setPos(self.cube_x + self.cube_u, self.cube_y + self.cube_u*2, self.cube_z + self.cube_u)
        self.cube_n.setHpr(self.cube_h, self.cube_p, self.cube_r)
        #3 cube_e
        self.cube_e.setPos(self.cube_x + self.cube_u*2, self.cube_y + self.cube_u, self.cube_z + self.cube_u)
        self.cube_e.setHpr(self.cube_h, self.cube_p, self.cube_r)
        #4 cube_w
        self.cube_w.setPos(self.cube_x, self.cube_y + self.cube_u, self.cube_z + self.cube_u)
        self.cube_w.setHpr(self.cube_h, self.cube_p, self.cube_r)
        #5 cube_t
        self.cube_t.setPos(self.cube_x + self.cube_u, self.cube_y + self.cube_u, self.cube_z + self.cube_u*2)
        self.cube_t.setHpr(self.cube_h, self.cube_p, self.cube_r)
        #6 cube_b
        self.cube_b.setPos(self.cube_x + self.cube_u, self.cube_y + self.cube_u, self.cube_z)
        self.cube_b.setHpr(self.cube_h, self.cube_p, self.cube_r)
        # set Corner-Cubes
        #1 cube_tsw
        self.cube_tsw.setPos(self.cube_x, self.cube_y, self.cube_z + self.cube_u*2)
        self.cube_tsw.setHpr(self.cube_h, self.cube_p, self.cube_r)
        #2 cube_tse
        self.cube_tse.setPos(self.cube_x + self.cube_u*2, self.cube_y, self.cube_z + self.cube_u*2)
        self.cube_tse.setHpr(self.cube_h, self.cube_p, self.cube_r)
        #3 cube_ten
        self.cube_ten.setPos(self.cube_x + self.cube_u*2, self.cube_y + self.cube_u*2, self.cube_z + self.cube_u*2)
        self.cube_ten.setHpr(self.cube_h, self.cube_p, self.cube_r)
        #4 cube_twn
        self.cube_twn.setPos(self.cube_x, self.cube_y + self.cube_u*2, self.cube_z + self.cube_u*2)
        self.cube_twn.setHpr(self.cube_h, self.cube_p, self.cube_r)
        #5 cube_bsw
        self.cube_bsw.setPos(self.cube_x, self.cube_y, self.cube_z)
        self.cube_bsw.setHpr(self.cube_h, self.cube_p, self.cube_r)
        #6 cube_bse
        self.cube_bse.setPos(self.cube_x + self.cube_u*2, self.cube_y, self.cube_z)
        self.cube_bse.setHpr(self.cube_h, self.cube_p, self.cube_r)
        #7 cube_ben
        self.cube_ben.setPos(self.cube_x + self.cube_u*2, self.cube_y + self.cube_u*2, self.cube_z)
        self.cube_ben.setHpr(self.cube_h, self.cube_p, self.cube_r)
        #8 cube_bwn
        self.cube_bwn.setPos(self.cube_x, self.cube_y + self.cube_u*2, self.cube_z)
        self.cube_bwn.setHpr(self.cube_h, self.cube_p, self.cube_r)
        # set Edge-Cubes
        #1 cube-ts
        self.cube_ts.setPos(self.cube_x + self.cube_u, self.cube_y, self.cube_z + self.cube_u*2)
        self.cube_ts.setHpr(self.cube_h, self.cube_p, self.cube_r)
        #2 cube-te
        self.cube_te.setPos(self.cube_x + self.cube_u*2, self.cube_y + self.cube_u, self.cube_z + self.cube_u*2)
        self.cube_te.setHpr(self.cube_h, self.cube_p, self.cube_r)
        #3 cube-tw
        self.cube_tw.setPos(self.cube_x, self.cube_y + self.cube_u, self.cube_z + self.cube_u*2)
        self.cube_tw.setHpr(self.cube_h, self.cube_p, self.cube_r)
        #4 cube-tn
        self.cube_tn.setPos(self.cube_x + self.cube_u, self.cube_y + self.cube_u*2, self.cube_z + self.cube_u*2)
        self.cube_tn.setHpr(self.cube_h, self.cube_p, self.cube_r)
        #5 cube_bs
        self.cube_bs.setPos(self.cube_x + self.cube_u, self.cube_y, self.cube_z)
        self.cube_bs.setHpr(self.cube_h, self.cube_p, self.cube_r)
        #6 cube_be
        self.cube_be.setPos(self.cube_x + self.cube_u*2, self.cube_y + self.cube_u, self.cube_z)
        self.cube_be.setHpr(self.cube_h, self.cube_p, self.cube_r)
        #7 cube_bw
        self.cube_bw.setPos(self.cube_x, self.cube_y + self.cube_u, self.cube_z)
        self.cube_bw.setHpr(self.cube_h, self.cube_p, self.cube_r)
        #8 cube_bn
        self.cube_bn.setPos(self.cube_x + self.cube_u, self.cube_y + self.cube_u*2, self.cube_z)
        self.cube_bn.setHpr(self.cube_h, self.cube_p, self.cube_r)
        #9 cube_sw
        self.cube_sw.setPos(self.cube_x, self.cube_y, self.cube_z + self.cube_u)
        self.cube_sw.setHpr(self.cube_h, self.cube_p, self.cube_r)
        #10 cube_se
        self.cube_se.setPos(self.cube_x + self.cube_u*2, self.cube_y, self.cube_z + self.cube_u)
        self.cube_se.setHpr(self.cube_h, self.cube_p, self.cube_r)
        #11 cube_en
        self.cube_ne.setPos(self.cube_x + self.cube_u*2, self.cube_y + self.cube_u*2, self.cube_z + self.cube_u)
        self.cube_ne.setHpr(self.cube_h, self.cube_p, self.cube_r)
        #12 cube_nw
        self.cube_nw.setPos(self.cube_x, self.cube_y + self.cube_u*2, self.cube_z + self.cube_u)
        self.cube_nw.setHpr(self.cube_h, self.cube_p, self.cube_r)
    ############################################
    # Key-boad event habdler
    ############################################
    # arrow-key:move the camera's position
    #
    def move_camera(self):
        self.camera_z = self.camera_d*math.sin(self.camera_rz)
        rr = abs(self.camera_d*math.cos(self.camera_rz))
        self.camera_x = rr*math.cos(self.camera_rx)
        self.camera_y = rr*math.sin(self.camera_rx)
        #print(f"rr={rr:3.2f}")
        #print(f"({self.camera_x:3.2f}, {self.camera_y:3.2f}, {self.camera_z:3.2f})")
        self.camera.setPos(self.camera_x + self.cube_u*3/2, self.camera_y + self.cube_u*3/2, self.camera_z + self.cube_u*3/2) 
        self.camera.lookAt(self.cube_x + self.cube_u*3/2, self.cube_y + self.cube_u*3/2, self.cube_z + self.cube_u*3/2)

    #
    # home:reset the camera's position(front)
    #
    def reset_camera(self):
        if self.ope_mode[0] == RubikGame.PLAY_MODE:
            #self.camera_rz = math.radians(0)    # 0:horizontal -> 90:top
            #self.camera_rx = math.radians(270)  # 0:right -> 90:back -> 180:left ->270(front)
            #self.camera_rz = math.radians(-90)   # -90:bottom 
            #self.camera_rx = math.radians(90)    #  90:back
            self.camera_rz = math.radians(45)     # 45:up 
            self.camera_rx = math.radians(315)    # 45:right
            self.camera_d = 20                   # distance
            self.move_camera()
        return
    #
    # 'o':opposit position
    #
    def opposit_camera(self):
        if self.ope_mode[0] == RubikGame.PLAY_MODE:
            self.camera_rz += math.radians(180) # 0:horizontal -> 90:top
            self.camera_rx += math.radians(180) # 0:right -> 90:back -> 180:left ->270(front)
            self.camera_d = 20                  # distance
            self.move_camera()
        else:
            self.cli.input('o')
        return
    #
    def upside_down(self):
        print("upside_down")
        self.upsideDownFlag = (not self.upsideDownFlag)
        for cube in (self.cube1 + self.cube2 + self.cube3):
            cube.upsideDown(self.cube_u)
    #
    # arrow-key:move camera to down
    def down_key(self):
        self.camera_rz -= math.radians(5)
        self.move_camera()

    # arrow-key:move camera to up
    def up_key(self):
        self.camera_rz += math.radians(5)
        self.move_camera()

    # arrow-key:move camera to right
    def right_key(self):
        #if self.ope_mode[0] == RubikGame.PLAY_MODE:
            self.camera_rx += math.radians(5)
            self.move_camera()

    # arrow-key:move camera to left
    def left_key(self):
        #if self.ope_mode[0] == RubikGame.PLAY_MODE:
            self.camera_rx -= math.radians(5)
            self.move_camera()
    #
    # e/w/s/n/t/b:select a face relatively 
    #
    def top_face(self, key = 't'):
        if self.ope_mode[0] == RubikGame.PLAY_MODE:
            self.selected_face = key
            if len(self.subBuffer) > 0:
                self.subBuffer.append(key)
        else:
            self.cli.input(key)
        return
    def bottom_face(self, key = 'b'):
        if self.ope_mode[0] == RubikGame.PLAY_MODE:
            self.selected_face = key
            if len(self.subBuffer) > 0:
                self.subBuffer.append(key)
        else:
            self.cli.input(key)
        return
    def south_face(self, key = 's'):
        if self.ope_mode[0] == RubikGame.PLAY_MODE:
            self.selected_face = key
            if len(self.subBuffer) > 0:
                self.subBuffer.append(key)
        else:
            self.cli.input(key)
        return
    def north_face(self, key = 'n'):
        if self.ope_mode[0] == RubikGame.PLAY_MODE:
            self.selected_face = key
            if len(self.subBuffer) > 0:
                self.subBuffer.append(key)
        else:
            self.cli.input(key)
        return
    def east_face(self, key = 'e'):
        if self.ope_mode[0] == RubikGame.PLAY_MODE:
            self.selected_face = key
            if len(self.subBuffer) > 0:
                self.subBuffer.append(key)
        else:
            self.cli.input(key)
        return
    def west_face(self, key = 'w'):
        if self.ope_mode[0] == RubikGame.PLAY_MODE:
            self.selected_face = key
            if len(self.subBuffer) > 0:
                self.subBuffer.append(key)
        else:
            self.cli.input(key)
        return
    #
    # O/R/G/B/Y/W:select a face absolutely 
    #
    def orange_face(self):
        if self.ope_mode[0] == RubikGame.PLAY_MODE:
            self.east_face('E')
        else:
            self.cli.input('O')
        return
    def red_face(self):
        if self.ope_mode[0] == RubikGame.PLAY_MODE:
            self.west_face('W')
        else:
            self.cli.input('R')
        return
    def green_face(self):
        if self.ope_mode[0] == RubikGame.PLAY_MODE:
            self.south_face('S')
        else:
            self.cli.input('G')
        return
    def blue_face(self):
        if self.ope_mode[0] == RubikGame.PLAY_MODE:
            self.north_face('N')
        else:
            self.cli.input('B')
        return
    def yellow_face(self):
        if self.ope_mode[0] == RubikGame.PLAY_MODE:
            self.top_face('T')
        else:
            self.cli.input('Y')
        return
    def white_face(self):
        if self.ope_mode[0] == RubikGame.PLAY_MODE:
            self.bottom_face('B')
        else:
            self.cli.input('W')
        return
    #
    # event handler of key-press for rotate the face selected
    # 
    def right_char(self, undo = False):     #'+(;)'
        if self.ope_mode[0] == RubikGame.PLAY_MODE:
            if len(self.subBuffer) == 0:
                self.right_rotate(undo) 
            else:
                self.subBuffer.append('+')
                self.cmd_sequence()
        else:
            self.cli.input('+')
        return
    #
    def left_char(self, undo = False):      #'-'
        if self.ope_mode[0] == RubikGame.PLAY_MODE:
            if len(self.subBuffer) == 0:
                self.left_rotate(undo) 
            else:
                self.subBuffer.append('-')
                self.cmd_sequence()
        else:
            self.cli.input('-')
        return
    # 
    # escape-key:suspend current seaquence
    #  
    def escape(self):
        if self.ope_mode[0] == RubikGame.PLAY_MODE:
            self.write_opelog('esc')
            self.selected_face = None
            self.undoPos = None
            if self.restartFlag == True:
                self.restartFlag = False
            if self.autoStart:
                print(f"\nauto start suspended")
                self.write_opelog('auto start suspended')
                self.taskMgr.remove("autoTask")
                self.autoStart = False
                self.preDt = 0
            if self.read_fd != None:
                self.read_fd.close()
                self.read_fd = None
                self.read_count = 0
            self.cli.clrPrompt()
            self.cli.clear()
        if self.ope_mode[0] == RubikGame.SET_MODE:
            if self.cmdfileSetting or self.cmdKeyinSetting:
                self.cmdfileSetting = False
                self.cmdKeyinSetting = False
                self.ope_mode[0] = RubikGame.PLAY_MODE
                self.cli.clear()
        return
    # 
    # enter-key:confirm the commands in cmdline.
    #
    def confirm(self):
        if self.ope_mode[0] == RubikGame.PLAY_MODE:
            self.write_opelog('confirm')
            # save cmdBuffer to log-file
            if len(self.cmdBuffer) > 0:
                self.write_cmdlog(self.cmdBuffer)
                # clear cmdBuffer
                self.cmdBuffer = []
                self.undoPos == None

                cmdline = '操作ログ：'
                self.cmdline.setText(cmdline)
                self.cli.clear()
            # regist current cube's attr(conf,pos)
            if self.setting[1] == '1': # auto-reg.
                self.regCubeAttr(self.cube2, './reg/cube2')
                self.regCubeAttr(self.cube3, './reg/cube3')
                
                self.regfile = f"{time.strftime('%Y%m%d%H%M%S')}"
                self.regCubeAttr(self.cube2+self.cube3, f"./reg/{self.regfile}")
                self.write_opelog(f"regCubeID:{self.regfile}")
            if self.setting[2] == '1': # auto-search
                self.pattern_search(1)
        else:
            if self.cmdfileSetting:
                # after selection of command-file
                self.cmdfile = self.cli.getBuffer()
                self.cmdfileSetting = False
                self.ope_mode[0] = RubikGame.PLAY_MODE
                self.cli.clrPrompt()
                self.cli.start()

                # excute the first line command in command-file
                self.write_opelog(f"read_file:{self.cmdfile}")
                try:
                    self.read_fd = open(self.cmdfile, mode='r')
                except:
                    print(f"{self.cmdfile} not found.")
                    self.cli.prompt(f">ファイル({self.cmdfile})がありません。\n"\
                                    " escキーで中断してください。")
                else:
                    self.readf_next()
                    self.cli.prompt(">spaceキーで次行のコマンドを実行します。\n"\
                                    " ctrl-aキーで最終行まで実行します。\n"\
                                    " escキーで中断します。")
            elif self.cmdKeyinSetting:
                self.cmdKeyinSetting = False
                self.ope_mode[0] = RubikGame.PLAY_MODE
                #
                self.write_opelog(f"input_cmd:{self.cli.getBuffer()}")
                # execute command in input-line
                self.do_cmdline(self.cli.getBuffer())
                if self.cur_mode == RubikGame.PLAY_MODE:
                    self.cli.clear()
                if self.cur_mode == RubikGame.SET_MODE:
                    self.ope_mode[0] = RubikGame.SET_MODE
                    self.cli.start()
            else:
                # execute CLI command
                self.do_cli(self.cli.getBuffer())
                self.cli.start()
        return
    #  
    # u-key:undo the last command.
    #
    def undo(self):
        if self.ope_mode[0] == RubikGame.PLAY_MODE:
            # search un-do command position in cmd. buffer
            if self.undoPos == None:
                self.undoPos = len(self.cmdBuffer)
            elif self.undoPos > 0:
                self.undoPos -= 1
            #
            print(f"undoPos = {self.undoPos}")
            if self.undoPos  > 0:
                # execute un-do command 
                cmd = self.cmdBuffer[self.undoPos-1]
                self.selected_face = cmd[0]
                if cmd[1] == '-':
                    self.right_rotate(undo = True)
                else:
                    self.left_rotate(undo = True)
            else:
                self.undoPos = 0
        else:
            self.cli.input('u')
        #
        return self.undoPos
    #
    # ctrl+z:cancel un-comfirmed commands.
    #   
    def cancel(self):
        cur_mode = self.ope_mode[0]
        if cur_mode != RubikGame.PLAY_MODE:
            self.ope_mode[0] = RubikGame.PLAY_MODE
        
        i = self.undo()
        while i > 0:
               i = self.undo()
        #
        if cur_mode == RubikGame.PLAY_MODE:
            self.write_opelog('cancel -> confirm')
            self.confirm()
        #        
        self.ope_mode[0] = cur_mode
        return
    #
    # ctlr+i:input commands with key and execute.
    #  
    def input_cmd(self):
        self.cmdKeyinSetting = True
        self.ope_mode[0] = RubikGame.SET_MODE
        self.cli.start(">コマンドを入力してください。!!\n"\
                            " enterキーで入力コマンドを実行します。\n")
    #
    # ctlr+c:copy commands to work-buffer.
    #
    def copy_cmd(self):
        self.copyBuffer = self.cmdBuffer
    #
    # ctlr+p:past work-buffer to input-line.
    #
    def past_input(self):
        self.cmdKeyinSetting = True
        self.ope_mode[0] = RubikGame.SET_MODE
        self.cli.start("> enterキーで入力コマンドを実行します。\n")
        for cmd in self.copyBuffer:
            self.cli.append(cmd)
    #
    # ctlr+f:read command from command-file and execute.
    #  
    def read_file(self):
        self.cmdfileSetting = True
        self.ope_mode[0] = RubikGame.SET_MODE
        self.cli.start(">コマンドファイル名を入力してください。!!\n"\
                            " enterキーで先頭行のコマンドを実行します。\n")
        self.cli.append(self.cmdfile)
    #
    # ctlr+a:read next a record and execute by auto timer.
    #  
    def auto_start(self):
        if self.read_fd == None:
            return
        self.write_opelog(f"auto start")
        # start autotask
        self.taskMgr.remove("autoTask")
        self.mainLoop = self.taskMgr.add(self.autoTask, "autoTask")
        self.autoStart = True
    #
    #  left-bottom click
    #
    def mouse1_click(self):
        if self.mouseWatcherNode.hasMouse:
            if self.ope_mode[0] == RubikGame.PLAY_MODE and self.restartFlag == True:
                x = self.mouseWatcherNode.getMouseX()
                y = self.mouseWatcherNode.getMouseY()
                print(f"mouse left button click:int(*100)!!({int(x*100)},{int(y*100)})")
                #
                self.random_start(abs(int(x*100)), abs(int(y*100)))
        return
    #
    # bs-key: cancel the last char.
    #
    def backspace_key(self):
        if self.ope_mode[0] != RubikGame.PLAY_MODE:
            self.cli.input('\b')
        return
    #
    # persent-key: cancel the last char.
    #
    def persent_key(self):
        if self.ope_mode[0] != RubikGame.PLAY_MODE:
            self.cli.input('%')
        return
    #
    # del-key: cancel inputline.
    #
    def delete_key(self):
        if self.ope_mode[0] != RubikGame.PLAY_MODE:
            self.cli.input('')
        return
    #
    # space-key: read the next record from opened cmdfile.
    #
    def space_key(self):
        if self.ope_mode[0] == RubikGame.PLAY_MODE:
            if self.read_fd != None:
                if self.readf_next() == None:
                    self.cli.prompt('')
                else:
                    self.cli.prompt(">spaceキーで次行のコマンドを実行します。\n"\
                                    " ctrl-aキーで最終行まで実行します。\n"\
                                    " escキーで中断します。")
        else:
            self.cli.input(' ')
        return
    #
    # right arrow-key(not repeat): move the cursor to right in input-line.
    #     
    def cursor_right(self):
        if self.ope_mode[0] == RubikGame.SET_MODE:
            self.cli.input('\t')
        return
    #
    # left arrow-key(not repeat): move the cursor to left in input-line.
    #     
    def cursor_left(self):
        if self.ope_mode[0] == RubikGame.SET_MODE:
            self.cli.input('\v')
        return
    #
    # other alphabet-key
    #
    def a_key(self):
        if self.ope_mode[0] != RubikGame.PLAY_MODE:
            self.cli.input('a')
    def c_key(self):
        if self.ope_mode[0] != RubikGame.PLAY_MODE:
            self.cli.input('c')
    def d_key(self):
        if self.ope_mode[0] != RubikGame.PLAY_MODE:
            self.cli.input('d')
    def f_key(self):
        if self.ope_mode[0] != RubikGame.PLAY_MODE:
            self.cli.input('f')
    def g_key(self):
        if self.ope_mode[0] != RubikGame.PLAY_MODE:
            self.cli.input('g')
    def h_key(self):
        if self.ope_mode[0] != RubikGame.PLAY_MODE:
            self.cli.input('h')
    def i_key(self):
        if self.ope_mode[0] != RubikGame.PLAY_MODE:
            self.cli.input('i')
    def j_key(self):
        if self.ope_mode[0] != RubikGame.PLAY_MODE:
            self.cli.input('j')
    def k_key(self):
        if self.ope_mode[0] != RubikGame.PLAY_MODE:
            self.cli.input('k')
    def l_key(self):
        if self.ope_mode[0] != RubikGame.PLAY_MODE:
            self.cli.input('l')
    def m_key(self):
        if self.ope_mode[0] != RubikGame.PLAY_MODE:
            self.cli.input('m')
    def r_key(self):
        if self.ope_mode[0] != RubikGame.PLAY_MODE:
            self.cli.input('r')
    def p_key(self):
        if self.ope_mode[0] != RubikGame.PLAY_MODE:
            self.cli.input('p')
    def q_key(self):
        if self.ope_mode[0] != RubikGame.PLAY_MODE:
            self.cli.input('q')
    def upper_s(self):
        if self.ope_mode[0] != RubikGame.PLAY_MODE:
            self.cli.input('S')
    def upper_e(self):
        if self.ope_mode[0] != RubikGame.PLAY_MODE:
            self.cli.input('E')
    def upper_n(self):
        if self.ope_mode[0] != RubikGame.PLAY_MODE:
            self.cli.input('N')
    def upper_t(self):
        if self.ope_mode[0] != RubikGame.PLAY_MODE:
            self.cli.input('T')
    def v_key(self):
        if self.ope_mode[0] != RubikGame.PLAY_MODE:
            self.cli.input('v')
        else:
            self.cmd_sequence_char('v')
    def x_key(self):
        if self.ope_mode[0] != RubikGame.PLAY_MODE:
            self.cli.input('x')
    def y_key(self):
        if self.ope_mode[0] != RubikGame.PLAY_MODE:
            self.cli.input('y')
        else:
            self.cmd_sequence_char('y')
    def z_key(self):
        if self.ope_mode[0] != RubikGame.PLAY_MODE:
            self.cli.input('z')
        else:
            self.cmd_sequence_char('z')
    def comma_key(self):
        if self.ope_mode[0] != RubikGame.PLAY_MODE:
            if self.cmdKeyinSetting:
                self.cli.input('<')
            else:
                self.cli.input(',')
        else:
            self.cmd_sequence_char('<')
    def dot_key(self):
        if self.ope_mode[0] != RubikGame.PLAY_MODE:
            if self.cmdKeyinSetting:
                self.cli.input('>')
            else:
                self.cli.input('.')
        else:
            self.cmd_sequence_char('>')
    def slash_key(self):
        if self.ope_mode[0] != RubikGame.PLAY_MODE:
            self.cli.input('/')
    def under_key(self):
        if self.ope_mode[0] != RubikGame.PLAY_MODE:
            self.cli.input('_')
    def num1_key(self):
        if self.ope_mode[0] != RubikGame.PLAY_MODE:
            self.cli.input('1')
    def num2_key(self):
        if self.ope_mode[0] != RubikGame.PLAY_MODE:
            self.cli.input('2')
    def num3_key(self):
        if self.ope_mode[0] != RubikGame.PLAY_MODE:
            self.cli.input('3')
    def num4_key(self):
        if self.ope_mode[0] != RubikGame.PLAY_MODE:
            self.cli.input('4')
    def num5_key(self):
        if self.ope_mode[0] != RubikGame.PLAY_MODE:
            self.cli.input('5')
    def num6_key(self):
        if self.ope_mode[0] != RubikGame.PLAY_MODE:
            self.cli.input('6')
    def num7_key(self):
        if self.ope_mode[0] != RubikGame.PLAY_MODE:
            self.cli.input('7')
    def num8_key(self):
        if self.ope_mode[0] != RubikGame.PLAY_MODE:
            self.cli.input('8')
    def num9_key(self):
        if self.ope_mode[0] != RubikGame.PLAY_MODE:
            self.cli.input('9')
    def num0_key(self):
        if self.ope_mode[0] != RubikGame.PLAY_MODE:
            self.cli.input('0')
    #
    # ctrl+s:start game
    #
    def re_start(self):
        self.write_opelog('restart')
        # set all cube to initial position
        self.set_initial_cube()
        self.undoPos == None
        # clear cmdBuffer
        self.cmdBuffer = []
        self.cmdline.setText('操作ログ：')

        self.cli.prompt(">任意の位置で左ボタンをクリックして下さい！！\n ランダムに並び替えます。\n"\
                            " ESCキーでキャンセルします。")
        self.restartFlag = True
    #
    # ctrl+r:restore cube's positon from reg-file
    #
    def restore(self):
        self.write_opelog('restore')
        self.restCubeAttr(self.cube2, "./reg/cube2")
        self.restCubeAttr(self.cube3, "./reg/cube3")
    #
    # ctrl+e:regist and exit
    #
    def exit(self):
        # save cmdBuffer to log-file
        if len(self.cmdBuffer) > 0:
            self.write_cmdlog(self.cmdBuffer)       
        # regist cube's attr(conf,pos)
        self.regCubeAttr(self.cube2, './reg/cube2')
        self.regCubeAttr(self.cube3, './reg/cube3')
        
        self.write_opelog('exit')
        sys.exit()
    #
    # ctrl+q:quit
    #
    def quit(self):
        # save cmdBuffer to log-file
        if len(self.cmdBuffer) > 0:
            self.write_cmdlog(self.cmdBuffer)
        #
        self.write_opelog('quit')
        sys.exit()
    #
    # analize input-line and execute
    #
    def do_cli(self, inputBuffer):
        self.write_opelog(f"do_cli:{inputBuffer}")
        cmd = inputBuffer.split(' ', 1)
        params = None
        if len(cmd) > 1:
            params = cmd[1].split(' ')
        if self.pattern_viewing:
            params = []
            params.append('v')
            params.append(cmd[0])
            cmd[0] = 'pt'
        #
        if self.ope_mode[0] == RubikGame.MENU_MODE:
            # setting memu
            if cmd[0].isdigit():
                num = int(cmd[0])
                if num == 0:
                    self.set_help_text()
                    self.cli.clrPrompt()
                    self.ope_mode[0] = RubikGame.SET_MODE
                elif num <= 2:
                    self.setting[num - 1] = params[0]
                    print(f"setting:{self.setting}")
                    self.cmdfile = f"{self.setting[0]}" 
                    # refresh menu
                    self.set_menu_text(True)
        else:
            # cli-command
            if cmd[0] == 'reg':     # regist current position of cube
                if params != None and len(params) > 0:
                    self.regCubeAttr(self.cube2+self.cube3, f"{params[0]}")
            elif cmd[0] == 'ld': # load cube position from reg. file
                if params != None and len(params) > 0:
                    self.restCubeAttr(self.cube2+self.cube3, f"{params[0]}")
            elif cmd[0] == 'lw': # write log-file
                if params != None:
                    if len(params) == 1:
                        self.logfile_write(params[0])
                    elif len(params) > 1:
                        self.logfile_write(params[0], params[1])
            elif cmd[0] == 'pt': # pattern reg/serach
                if params != None and len(params) > 0:
                    if params[0] == 'r':
                        self.pattern_reg(params)
                    elif params[0] == 's':
                        self.pattern_search()
                    elif params[0] == 'v':
                        if len(params) > 1:
                            self.pattern_view(params[1])
                    elif params[0] == 'd':
                        self.pattern_delete(params)
                    elif params[0] == 'g':
                        self.pattern_get(params)
            elif cmd[0] == 'set': # display the setting menu
                self.set_menu_text(False)
                self.ope_mode[0] = RubikGame.MENU_MODE
                self.cli.prompt(">メニュー番号と値を入力して下さい！！\n")
        #
        return
    #
    # read next a record and execute.
    #
    def readf_next(self):
        # read next record
        line = self.read_fd.readline()
        self.read_count += 1
        while line != '':
            if line[0] != '#':
                if line[-1] == '\n':
                    line = line[:len(line)-1]
                print(f"{self.read_count}:{line}")
                # execute command-line
                self.do_cmdline(line)
                break
            # read next record
            line = self.read_fd.readline()
            self.read_count += 1
        #
        if line == '':  # end of file
            print(f"\nread_file eof:{self.cmdfile}")
            self.write_opelog(f"read_file eof:{self.cmdfile}")
            self.read_fd.close()
            self.read_fd = None
            self.read_count = 0
            if self.autoStart:
                print(f"auto start stopped.")
                self.write_opelog(f"auto start stopped.")
                # stop autoTask
                self.taskMgr.remove("autoTask")
                self.autoStrt = False
                self.preDt = 0
                self.cli.clear()
        return self.read_fd
    #
    # write logfile with another file.
    #
    def logfile_write(self, fname, span = None):
        #
        # analize from-to parameter
        #
        from_no = 1
        to_no = None
        if span != None:
            if span[0] == '-' and span[1:].isdigit():
                to_no = int(span[1:]) - 1
            else:
                from_to = span.split('-')
                if from_to[0].isdigit():
                    from_no = int(from_to[0]) - 1
                    if len(from_to) > 1 and from_to[1].isdigit():
                        to_no = int(from_to[1]) - 1
        #
        # copy some records from default log-file to specified file.
        #
        out_fd = open(fname, mode='a')
        with open(self.logfile, 'r') as fd:
            for lno, line in enumerate(fd):
                if to_no != None and  lno > to_no: 
                    break
                if lno >= from_no: 
                    out_fd.write(line)
            #
        #
        fd.close()
        out_fd.close()
        return
    #
    # excetue commands in command-line
    #    {<face-id>[<seq-ope>][<face-id>]<direction>}...
    #       <face-id>  ::{'t'|'b'|'s'|'n'|'e'|'w'}
    #       <seq-ope>::{'y'|'z'|'v'|'>'|'<'}
    #       <direction>::{'+'|'-'}
    #
    def do_cmdline(self, cmdline):
        print(f"do_cmdline:{cmdline}")
        if len(cmdline)%2 != 0:
            print(f"do_cmdline:length error!!")
            return
        is_seq = False
        for i in range(0, len(cmdline), 2):
            if is_seq:
                # execute seq-command.
                self.cmd_sequence()
                is_seq = False
            else:
                is_seq = False
                self.selected_face = cmdline[i]
                if cmdline[i+1] == '+':
                    self.right_rotate()
                elif cmdline[i+1] == '-':
                    self.left_rotate()
                else:   #'y'/'z'/'v'/'>'/'<'
                    self.cmd_sequence_char(cmdline[i+1])
                    self.subBuffer.append(cmdline[i+2])
                    self.subBuffer.append(cmdline[i+3])
                    is_seq = True
        #
        #
        self.cli.clear()
        return
    #
    # excetue rotate-commands in command-buffer
    #
    def do_command(self, cmdbuf):
        for cmd in cmdbuf:
            self.selected_face = cmd[0]
            if cmd[1] == '+':
                self.right_rotate()
            elif cmd[1] == '-':
                self.left_rotate()
            else:
                print(f"do_command:direction[{cmd[1]}] error!!")
        return
    #
    #  execute randam command(move all cubes to game position)
    #
    def random_start(self, randx, randy):
        face = ['s', 'n', 'e', 'w', 't', 'b']
        direct = ['+', '-']
        cmdbuf = []

        print('random_start!!')
        # create random commands into buffer
        for i in range(1, min(randx, randy)):
            fi = random.randint(1,6)
            di = random.randint(1,2)
            cmd = f"{face[fi-1]}{direct[di-1]}"
            cmdbuf.append(cmd)

        # excecute these commands
        self.do_command(cmdbuf)
        self.cli.prompt('>enterキーを押して開始します。')
        self.restartFlag = False
        return

    #
    # store cmd-char[y/z/v/<(,)/>(.)] to buffer
    #
    def cmd_sequence_char(self, char):
        self.subBuffer = []
        self.subBuffer.append(self.selected_face)
        self.subBuffer.append(char)
    #
    # execute sequence-cmd.
    #
    def cmd_sequence(self):
        print(f"cmd_sequence:{self.subBuffer}")
        if self.subBuffer[1] != 'v' and len(self.subBuffer) < 4:
            print(f"cmd_sequence:syntax error!!")
        else:
            if self.subBuffer[1] == 'y':    #Y-exchange
                self.cmd_seq_exchange_y()            
            elif self.subBuffer[1] == 'z':  #Z-exchange
                self.cmd_seq_exchange_z()            
            elif self.subBuffer[1] == 'v':  #disinter
                self.cmd_seq_disinter()            
            elif self.subBuffer[1] == '<':  #world around(,)
                self.cmd_seq_around()            
            elif self.subBuffer[1] == '>':  #world around(.)
                self.cmd_seq_around()            
            else:
                print(f"cmd_sequence:direction[{self.subBuffer[1]}] error!!")
        #
        self.subBuffer = ''
        return
    #
    #   Y-exchange ('sye+')
    #
    def cmd_seq_exchange_y(self):
        self.selected_face = self.subBuffer[0]
        if self.subBuffer[3] == '+':
            self.right_rotate()
        else:
            self.left_rotate()
        #
        self.selected_face = self.subBuffer[2]
        if self.subBuffer[3] == '+':
            self.left_rotate()
        else:
            self.right_rotate()
        #
        self.selected_face = self.subBuffer[0]
        if self.subBuffer[3] == '+':
            self.left_rotate()
        else:
            self.right_rotate()
        self.selected_face = self.subBuffer[2]
        if self.subBuffer[3] == '+':
            self.right_rotate()
        else:
            self.left_rotate()
        return
    #
    #   Z-exchange('sze+')
    #
    def cmd_seq_exchange_z(self):
        self.selected_face = self.subBuffer[0]
        if self.subBuffer[3] == '+':
            self.right_rotate()
        else:
            self.left_rotate()
        #
        self.selected_face = self.subBuffer[2]
        if self.subBuffer[3] == '+':
            self.right_rotate()
        else:
            self.left_rotate()
        #
        self.selected_face = self.subBuffer[0]
        if self.subBuffer[3] == '+':
            self.left_rotate()
        else:
            self.right_rotate()
        #
        self.selected_face = self.subBuffer[2]
        if self.subBuffer[3] == '+':
            self.left_rotate()
        else:
            self.right_rotate()
        return
    #
    #   Disintermediation('sv+')
    #
    def cmd_seq_disinter(self):
        self.selected_face = self.subBuffer[0]
        if self.subBuffer[2] == '+':
            self.right_rotate()
        else:
            self.left_rotate()
        #
        self.selected_face = RubikCube.getPairFace(self.subBuffer[0])
        if self.subBuffer[2] == '+':
            self.left_rotate()
        else:
            self.right_rotate()
        return
    #
    #   around world('e.s+')
    #
    def cmd_seq_around(self):
        fs = self.subBuffer[0]
        fe = self.subBuffer[2]
        faces = [fs, RubikCube.getPairFace(fe), RubikCube.getPairFace(fs), fe ]
        for face in faces:
            self.selected_face = face
            if self.subBuffer[3] == '+':
                self.right_rotate()
            else:
                self.left_rotate()
        return
    #
    # convert relative face-symbole to absolute face-symbol.
    #
    def rel2abs(self, face):
        rel_south  = ['e', 'n', 'w', 's']
        abs_faceN  = ['s', 'e', 'n', 'w', 's', 'e', 'n', 'w']
        abs_faceR  = ['n', 'e', 's', 'w', 'n', 'e', 's', 'w']
        
        # specified face-symbol absolutely
        if face.isupper():
            # convert to  lower case  
            return face.lower()
        #
        # convert top/bottom face-symbol
        #
        if face == 't' or face == 'b':
            if self.upsideDownFlag:
                # swap the symbol of top and bottom
                if face == 't':
                    face = 'b'
                else:
                    face = 't'
            return face
        #
        # serach the relative symbol of face on south
        #
        rx = self.camera_rx
        if self.camera_rx < 0.0:
            rx = 2*math.pi - abs(self.camera_rx)%(2*math.pi) 
        #
        idx_south = int((rx/(math.pi/2))%4)
        rel_sym = rel_south[idx_south]
        #print(f"south:{rel_sym}[{idx_south}]")
        #
        # convert the relative specified face-symbol to the absolute face-symbol 
        #
        rel_face = abs_faceN
        idx_south = rel_face.index(rel_sym) # index of relative symbol on south
        idx_face = rel_face.index(face)     # index of specified face  
        #
        idx = idx_face + idx_south
        if not self.upsideDownFlag:
            abs_face = abs_faceN
        else:
            abs_face = abs_faceR
        #print(f"{rel_sym}[{idx_south}]:{face}[{idx_face}] -> {abs_face[idx]}[{idx}]")
        return abs_face[idx]
    #
    #  execute right-rotate selected face
    #
    def right_rotate(self, undo = False): #'+(;)'
        #print(f"right_rotate!! selected face:{self.selected_face}")
        if self.selected_face != None:
            # convert relative symbol(low-case) to absolute symbol
            selected_face = self.rel2abs(self.selected_face)
            self.rotate_face(selected_face, 'r')
            if undo == False:
                self.undoPos = None
            #
            self.cmdBuffer.append(f"{selected_face.upper()}+")
            cmdline = '操作ログ：'
            for cmd in self.cmdBuffer:
                cmdline += cmd
            self.cmdline.setText(cmdline)
        #
        if self.is_completed(self.cube2+self.cube3):
            print('completed now!!')
            # save cmdBuffer to log-file
            self.confirm()
            self.write_opelog('completed now!!')
        return
    #
    #  execute left-rotate selected face
    #
    def left_rotate(self, undo = False): #'-'
        #print(f"left_rotate!! selected face:{self.selected_face}")
        if self.selected_face != None:
            # convert relative symbol(low-case) to absolute symbol
            selected_face = self.rel2abs(self.selected_face)
            self.rotate_face(selected_face, 'l')
            if undo == False:
                self.undoPos = None
            #
            self.cmdBuffer.append(f"{selected_face.upper()}-")
            cmdline = '操作ログ：'
            for cmd in self.cmdBuffer:
                cmdline += cmd
            self.cmdline.setText(cmdline)
        #
        if self.is_completed(self.cube2+self.cube3):
            print('completed now!!')
            self.confirm()
            self.write_opelog('completed now!!')
        return
    #
    # execute face-rotation process
    #
    def rotate_face(self, face, dir):
        if face == 's' or face == 'n':
            self.rotate_sn(face, dir)
        elif face == 'e' or face == 'w':
            self.rotate_ew(face, dir)
        elif face == 't' or face == 'b':
            self.rotate_tb(face, dir)
        return
    #
    # rotation of South/North-face
    #
    def rotate_sn(self, face, dir):
        print(f"rotate_sn:{face}{dir}")
        # origin(X,Z) list of corner-cube
        origin3 = [ (self.cube_x,                 self.cube_z),
                    (self.cube_x,                 self.cube_z + self.cube_u*2),
                    (self.cube_x + self.cube_u*2, self.cube_z + self.cube_u*2),
                    (self.cube_x + self.cube_u*2, self.cube_z),
                ]
        # origin(X,Z) list of edge-cube
        origin2 = [ (self.cube_x,                 self.cube_z + self.cube_u),
                    (self.cube_x + self.cube_u,   self.cube_z + self.cube_u*2),
                    (self.cube_x + self.cube_u*2, self.cube_z + self.cube_u),
                    (self.cube_x + self.cube_u,   self.cube_z),
                ]
        # adjust face-symbol with upside-down
        if self.upsideDownFlag:
            if face == 's':
                face = 'n'
            else:
                face = 's'
        # South or North
        if face == 's':
            cube_c = [cube for cube in self.cube3 if cube.getY() == self.cube_y]
            cube_e = [cube for cube in self.cube2 if cube.getY() == self.cube_y]
        else:
            cube_c = [cube for cube in self.cube3 if cube.getY() == self.cube_y + self.cube_u*2]
            cube_e = [cube for cube in self.cube2 if cube.getY() == self.cube_y + self.cube_u*2]

        #
        # arrange the corner-cube
        #
        if face == 's': #South
            if dir == 'r':  # Right(+)
                self.rarrange_XZ(cube_c, origin3)
            else:           # Left(-)
                self.larrange_XZ(cube_c, origin3)
        else:           #North
            if dir == 'r':  # Right(+)
                self.larrange_XZ(cube_c, origin3)
            else:           # Left(-)
                self.rarrange_XZ(cube_c, origin3)
        #
        # arrange the edge-cube
        #
        if face == 's': #South
            if dir == 'r':  # Right(+)
                self.rarrange_XZ(cube_e, origin2)
            else:           # Left(-)
                self.larrange_XZ(cube_e, origin2)
        else:           #North
            if dir == 'r':  # Right(+)
                self.larrange_XZ(cube_e, origin2)
            else:           # Left(-)
                self.rarrange_XZ(cube_e, origin2)
        return
    #
    # rotation of East/West-face
    #
    def rotate_ew(self, face, dir):
        print(f"rotate_ew:{face}{dir}")
        # origin(Y,Z) list of corner-cube
        origin3 = [ (self.cube_y,                 self.cube_z),
                    (self.cube_y,                 self.cube_z + self.cube_u*2),
                    (self.cube_y + self.cube_u*2, self.cube_z + self.cube_u*2),
                    (self.cube_y + self.cube_u*2, self.cube_z),
                ]
        # origin(Y,Z) list of edge-cube
        origin2 = [ (self.cube_y,                 self.cube_z + self.cube_u),
                    (self.cube_y + self.cube_u,   self.cube_z + self.cube_u*2),
                    (self.cube_y + self.cube_u*2, self.cube_z + self.cube_u),
                    (self.cube_y + self.cube_u,   self.cube_z),
                ]
        # East or West
        if face == 'e':
            cube_c = [cube for cube in self.cube3 if cube.getX() == self.cube_x + self.cube_u*2]
            cube_e = [cube for cube in self.cube2 if cube.getX() == self.cube_x + self.cube_u*2]
        else:
            cube_c = [cube for cube in self.cube3 if cube.getX() == self.cube_x]
            cube_e = [cube for cube in self.cube2 if cube.getX() == self.cube_x]
        #
        # arrange the corner-cube
        #
        if face == 'e': #East
            if dir == 'r':  # Right(+)
                self.rarrange_YZ(cube_c, origin3)
            else:           # Left(-)
                self.larrange_YZ(cube_c, origin3)
        else:           #West
            if dir == 'r':  # Right(+)
                self.larrange_YZ(cube_c, origin3)
            else:           # Left(-)
                self.rarrange_YZ(cube_c, origin3)
        #
        # arrange the edge-cube
        #
        if face == 'e': #East
            if dir == 'r':  # Right(+)
                self.rarrange_YZ(cube_e, origin2)
            else:           # Left(-)
                self.larrange_YZ(cube_e, origin2)
        else:           #West
            if dir == 'r':  # Right(+)
                self.larrange_YZ(cube_e, origin2)
            else:           # Left(-)
                self.rarrange_YZ(cube_e, origin2)
        return
    #
    # rotation of Top/Bottom-face
    #
    def rotate_tb(self, face, dir):
        print(f"rotate_tb:{face}{dir}")
        # origin(X,Y) list of corner-cube
        origin3 = [ (self.cube_x,                 self.cube_y),
                    (self.cube_x,                 self.cube_y + self.cube_u*2),
                    (self.cube_x + self.cube_u*2, self.cube_y + self.cube_u*2),
                    (self.cube_x + self.cube_u*2, self.cube_y),
                ]
        # origin(X,Y) list of edge-cube
        origin2 = [ (self.cube_x,                 self.cube_y + self.cube_u),
                    (self.cube_x + self.cube_u,   self.cube_y + self.cube_u*2),
                    (self.cube_x + self.cube_u*2, self.cube_y + self.cube_u),
                    (self.cube_x + self.cube_u,   self.cube_y),
                ]
        # adjust face-symbol with upside-down
        if self.upsideDownFlag:
            if face == 't':
                face = 'b'
            else:
                face = 't'
        # Top or Bottom
        if face == 't':     
            cube_c = [cube for cube in self.cube3 if cube.getZ() == self.cube_z + self.cube_u*2]
            cube_e = [cube for cube in self.cube2 if cube.getZ() == self.cube_z + self.cube_u*2]
        else:               
            cube_c = [cube for cube in self.cube3 if cube.getZ() == self.cube_z]
            cube_e = [cube for cube in self.cube2 if cube.getZ() == self.cube_z]       
        #
        # arrange the corner-cube
        #
        if face == 't': #Top
            if dir == 'r':  # Right(+) 
                self.rarrange_XY(cube_c, origin3)
            else:           # Left(-)
                self.larrange_XY(cube_c, origin3)
        else:           #Bottom
            if dir == 'r':  # Right(+)
                self.larrange_XY(cube_c, origin3)
            else:           # Left(-)
                self.rarrange_XY(cube_c, origin3)
        #
        # arrange the edge-cube
        if face == 't': #Top
            if dir == 'r':  # Right(+)
                self.rarrange_XY(cube_e, origin2)
            else:           # Left(-)
                self.larrange_XY(cube_e, origin2)
        else:           #Bottom
            if dir == 'r':  # Right(+)
                self.larrange_XY(cube_e, origin2)
            else:           # Left(-)
                self.rarrange_XY(cube_e, origin2)
        return
    #
    # move origin of cube and rotation in case of right-rotete 'S' or 'N' face
    #
    def rarrange_XZ(self, cube_c, origin_l):
        #print(f"rarrange_XZ")
        for cube in cube_c :
            X = cube.getX()
            Z = cube.getZ()
            hpr = cube.getHpr()
            #print(f"{cube.getId()}=({X}, {cube.getY()}, {Z}) Hpr:{hpr}")
            # move position
            origin = (X, Z)
            i = origin_l.index(origin)
            if i < len(origin_l) - 1:
                i += 1
            else:
                i = 0
            next = origin_l[i]
            cube.setX(next[0])
            cube.setZ(next[1])
            # rotation(Roll)
            cube.setDirR(90)
            #print(f"->  ({cube.getX()}, {cube.getY()}, {cube.getZ()}) Hpr:{cube.getHpr()}")
        return

    #
    # move origin of cube and rotation in case of left-rotate 'S' or 'N' face
    #
    def larrange_XZ(self, cube_c, origin_l):
        #print(f"larrange_XZ")
        for cube in cube_c :
            X = cube.getX()
            Z = cube.getZ()
            hpr = cube.getHpr()
            #print(f"{cube.getId()}=({X}, {cube.getY()}, {Z}) Hpr:{hpr}")
            # move position
            origin = (X, Z)
            i = origin_l.index(origin)
            if i > 0:
                i -= 1
            else:
                i = len(origin_l) - 1
            next = origin_l[i]
            cube.setX(next[0])
            cube.setZ(next[1])
            # rotation(Roll)
            cube.setDirR(-90)
            #print(f"->  ({cube.getX()}, {cube.getY()}, {cube.getZ()}) Hpr:{cube.getHpr()}")
        return
    #
    # move origin of cube and rotation in case of right-rotate 'E' or 'W' face
    #
    def rarrange_YZ(self, cube_c, origin_l):
        #print(f"rarrange_YZ")
        for cube in cube_c :
            Y = cube.getY()
            Z = cube.getZ()
            hpr = cube.getHpr()
            #print(f"{cube.getId()}=({cube.getX()}, {Y}, {Z}) Hpr:{hpr}")
            # move position
            origin = (Y, Z)
            i = origin_l.index(origin)
            if i < len(origin_l) - 1:
                i += 1
            else:
                i = 0
            next = origin_l[i]
            cube.setY(next[0])
            cube.setZ(next[1])
            # rotation(Pitch)
            cube.setDirP(-90)
            #print(f"->  ({cube.getX()}, {cube.getY()}, {cube.getZ()}) Hpr:{cube.getHpr()}")
        return

    #
    # move origin of cube and rotation in case of left-rotate 'E' or 'W' face
    #
    def larrange_YZ(self, cube_c, origin_l):
        #print(f"larrange_YZ")
        for cube in cube_c :
            Y = cube.getY()
            Z = cube.getZ()
            hpr = cube.getHpr()
            #print(f"{cube.getId()}=({cube.getX()}, {Y}, {Z}) Hpr:{hpr}")
            # move position
            origin = (Y, Z)
            i = origin_l.index(origin)
            if i > 0:
                i -= 1
            else:
                i = len(origin_l) - 1
            next = origin_l[i]
            cube.setY(next[0])
            cube.setZ(next[1])
            # rotation(Pitch)
            cube.setDirP(90)
            #print(f"->  ({cube.getX()}, {cube.getY()}, {cube.getZ()}) Hpr:{cube.getHpr()}")
        return
    #
    # move origin of cube and rotation in case of right-rotate 'T' or 'B' face
    #
    def rarrange_XY(self, cube_c, origin_l):
        #print(f"rarrange_XY")
        for cube in cube_c :
            X = cube.getX()
            Y = cube.getY()
            hpr = cube.getHpr()
            #print(f"{cube.getId()}=({X}, {Y}, {cube.getZ()}) Hpr:{hpr}")
            # move position
            origin = (X, Y)
            i = origin_l.index(origin)
            if i < len(origin_l) - 1:
                i += 1
            else:
                i = 0
            next = origin_l[i]
            cube.setX(next[0])
            cube.setY(next[1])
            # rotation(Headding)
            cube.setDirH(-90)
            #print(f"->  ({cube.getX()}, {cube.getY()}, {cube.getZ()}) Hpr:{cube.getHpr()}")
        return

    #
    # move origin of cube and rotation in case of left-rotate 'T' or 'B' face
    #
    def larrange_XY(self, cube_c, origin_l):
        #print(f"larrange_XY")
        for cube in cube_c :
            X = cube.getX()
            Y = cube.getY()
            hpr = cube.getHpr()
            #print(f"{cube.getId()}=({X}, {Y}, {cube.getZ()}) Hpr:{hpr}")
            # move position
            origin = (X, Y)
            i = origin_l.index(origin)
            if i > 0:
                i -= 1
            else:
                i = len(origin_l) - 1
            next = origin_l[i]
            cube.setX(next[0])
            cube.setY(next[1])
            # rotation(Headding)
            cube.setDirH(90)
            #print(f"->  ({cube.getX()}, {cube.getY()}, {cube.getZ()}) Hpr:{cube.getHpr()}")
        return
    #
    # regist all cube's attr{conf:,pos:} to reg.-file
    #
    def regCubeAttr(self, cube_list, fname):
        self.write_opelog(f"regCubeAttr:{fname}")
        attrs = []
        for cube in cube_list:
            attr = {'conf':cube.getConf(),
                    'pos':cube.getPos()}
            attrs.append(attr)
        #
        with open(f"{fname}.reg", 'wb') as fd:
            pickle.dump(attrs, fd, pickle.HIGHEST_PROTOCOL)
        return    
    #
    # restore all cube's attr{conf:,pos:} from reg.-file
    #
    def restCubeAttr(self, cube_list, fname):
        self.write_opelog(f"restCubeAttr:{fname}")
        try:
            with open(f"{fname}.reg", 'rb') as fd:
                attrs = pickle.load(fd)
        except:
            print(f"{fname}.reg not found.")
            return
        #print(f"attr:{attrs}")
        #
        i = 0
        for cube in cube_list:
            cube.setPosA(attrs[i].get('pos'))
            cube.setConf(attrs[i].get('conf'))
            i += 1
        #
        return    
    #
    # check if current configration of all cubes are completed.
    #
    def is_completed(self, cube_list):
        fname = './reg/completed'
        fnameA = './reg/completeda'
        try:
            with open(f"{fname}.reg", 'rb') as fd:
                ld_attrs = pickle.load(fd)
        except:
            print(f"{fname}.reg not found.")
            return
        try:
            with open(f"{fnameA}.reg", 'rb') as fd:
                ld_attrsA = pickle.load(fd)
        except:
            print(f"{fnameA}.reg not found.")
            return
        #
        cur_attrs = []
        for cube in cube_list:
            attr = {'conf':cube.getConf(),
                    'pos':cube.getPos()}
            cur_attrs.append(attr)
        #
        return (ld_attrs == cur_attrs) or (ld_attrsA == cur_attrs) 
    #
    # convert edge cube's-pos to db-item(pos)
    #
    def convPos2(self, pos):
        if pos[0] == (self.cube_x + self.cube_u):
            # Y('s' or 'n')
            if pos[1] == self.cube_y: # front
                position = 's'
            else:
                position = 'n'
        else:
            # X('w' or 'e')
            if pos[0] == self.cube_x: # left
                position = 'w'
            else: # right
                position = 'e'
            # Y('s' or 'n')
            if pos[1] == self.cube_y: # front
                position += 's'
            elif pos[1] == (self.cube_y+ self.cube_u*2): # rear
                position += 'n'
        #
        if len(position) == 1:    
            # Z('b' or 't')
            if pos[2] == self.cube_z: # bottom
                position += 'b'
            else:
                position += 't'
        #
        return position
    #
    def strPos2_val(self, pos):
        
        posStr =[ 
            'st', 'sb', 'nt', 'nb',
            'ws', 'wn', 'wt', 'wb',
            'es', 'en', 'et', 'eb'
        ]
        posVal =[
            (self.cube_x+self.cube_u, self.cube_y,               self.cube_z+self.cube_u*2),
            (self.cube_x+self.cube_u, self.cube_y,               self.cube_z),
            (self.cube_x+self.cube_u, self.cube_y+self.cube_u*2, self.cube_z+self.cube_u*2),
            (self.cube_x+self.cube_u, self.cube_y+self.cube_u*2, self.cube_z),
            
            (self.cube_x, self.cube_y,               self.cube_z+self.cube_u),
            (self.cube_x, self.cube_y+self.cube_u*2, self.cube_z+self.cube_u),
            (self.cube_x, self.cube_y+self.cube_u,   self.cube_z+self.cube_u*2),
            (self.cube_x, self.cube_y+self.cube_u,   self.cube_z),
            
            (self.cube_x+self.cube_u*2, self.cube_y,              self.cube_z+self.cube_u),
            (self.cube_x+self.cube_u*2, self.cube_y+self.cube_u*2,self.cube_z+self.cube_u),
            (self.cube_x+self.cube_u*2, self.cube_y+self.cube_u,  self.cube_z+self.cube_u*2),
            (self.cube_x+self.cube_u*2, self.cube_y+self.cube_u,  self.cube_z),
        ]
        return posVal[posStr.index(pos)]
    #
    # convert conner cube's-pos to db-item(pos)
    #
    def convPos3(self, pos):
        # X('w' or 'e')
        if pos[0] == self.cube_x: # left
            position = 'w'
        else:
            position = 'e'
        # Y('s' or 'n')
        if pos[1] == self.cube_y: # front
            position += 's'
        else:
            position += 'n'
        # Z('b' or 't')
        if pos[2] == self.cube_z: # bottom
            position += 'b'
        else:
            position += 't'
        return position
    #
    def strPos3_val(self, pos):
        # X('w' or 'e')
        if pos[0] == 'w': # left
            x = self.cube_x 
        else:             # right
            x = self.cube_x + self.cube_u*2
        # Y('s' or 'n')
        if pos[1] == 's': # front
            y = self.cube_y 
        else:
            y = self.cube_y + self.cube_u*2
        # Z('b' or 't')
        if pos[2] == 'b': # bottom
            z = self.cube_z 
        else:
            z = self.cube_z + self.cube_u*2
        return (x, y, z)
    #
    # convert cube's-conf to db-item(col)
    #
    def convCol(self, conf):
        # color number (TWS)
        return str(conf[0]) + str(conf[1]) + str(conf[2])
    #
    def strCol_conf(self, col):
        # color number (TWS)
        return (int(col[0]),int(col[1]),int(col[2]))
    #
    # convert db-item(pos2,col2) to edge cube's-attr  
    #
    def convAttr2(self, strPos, strCol):
        Attrs = []
        i = 0
        k = 0
        for _ in self.cube2:
            pos = self.strPos2_val(strPos[i:i+2])
            col = self.strCol_conf(strCol[k:k+3])
            i += 2
            k += 3
            attr = { 'pos': pos, 'conf' : col}
            Attrs.append(attr)
        return Attrs
    #
    # convert db-item(pos3,col3) to conner cube's-attr  
    #
    def convAttr3(self,  strPos, strCol):
        Attrs = []
        i = 0
        k = 0
        for _ in self.cube3:
            pos = self.strPos3_val(strPos[i:i+3])
            col = self.strCol_conf(strCol[k:k+3])
            i += 3
            k += 3
            attr = { 'pos': pos, 'conf' : col}
            Attrs.append(attr)
        return Attrs
    #
    # entry pattern-data to pattern-table in db
    #
    def entry_pattern(self, pt_id, attrs):
        pos_data = ''
        col_data = ''
        # edge cube
        idx = 0
        for _ in self.cube2:
            pos_data += self.convPos2(attrs[idx].get('pos'))
            col_data += self.convCol(attrs[idx].get('conf'))
            idx += 1
        cube2_attr = (pos_data, col_data)
        # conner cube
        pos_data = ''
        col_data = ''
        for _ in self.cube3:
            pos_data += self.convPos3(attrs[idx].get('pos'))
            col_data += self.convCol(attrs[idx].get('conf'))
            idx += 1
        cube3_attr = (pos_data, col_data)
        #
        return self.db.insert_pattern(pt_id, cube2_attr, cube3_attr)
    #
    # entry solution-data to solution-table in db
    #
    def entry_solution(self, pt_ids, cmd_line):
        for pt_id in pt_ids:
            sl_no = self.db.insert_solution(pt_id, cmd_line)
            print(f"entry_solution:{pt_id} - {sl_no}")

    #
    # registory of current cube-attr and cmd to db
    #
    def regPattern(self, fd):
        cancel_flg = False
        # read next record
        line = fd.readline()
        read_count = 1
        pt_id = []
        while line != '':
            if line[-1] == '\n':
                line = line[:len(line)-1]
            if '#regCubeID' in line:
                id = line[line.find(':')+1:]
                # execute command-line
                fname = f"./reg/{id}"
                try:
                    rfd = open(f"{fname}.reg", 'rb')
                except:
                    print(f"{fname}.reg not found.")
                    if pt_id:
                        self.db.rollback()
                    return
                else:
                    ld_attrs = pickle.load(rfd)
                    id = self.entry_pattern(id, ld_attrs)
                    pt_id.append(id)
                    print(f"entry_pattern({id}) at {read_count}:{line}")
            if '#completed' in line:
                self.db.commit_solution(pt_id)
                print(f"commit at {read_count}:{line}")
                pt_id = []
            if ('#restor' in line) or ('#quit' in line) or ('#exit' in line):
                if pt_id:
                    self.db.rollback()
                    print(f"rollback at {read_count}:{line}")
                    pt_id = []
                if ('#quit' in line) or ('#exit' in line):
                    break
            if ('#cancel' in line):
                cancel_flg = True
            if line[0] != '#':
                if pt_id and cancel_flg == False:
                    self.entry_solution(pt_id, line)
                    print(f"entry_solution at {read_count}")
                cancel_flg = False
            # read next record
            line = fd.readline()
            read_count += 1
        #
        if pt_id:
            self.db.rollback()
            print(f"rollback at {read_count}:eof")
        return
    #
    # registory cube's pattern and solution from log-file to db
    #
    def pattern_reg(self, params):
        print(f"pattern_reg:{params}")
        if len(params) > 1:
            fname = params[1]
        else:
            fname = self.logfile
        try:
            fd = open(fname, 'rt')
        except:
            print(f"{fname} not found.")
        else:   
            self.regPattern(fd)
            fd.close()
        return
    #
    # delete records from 'pattern'/'solutuin' table.
    #
    def pattern_delete(self, params):
        print(f"pattern_delete:{params}")
        match = None
        if len(params) > 1:
            match = params[1]
        self.db.delete_pattern(match)
        return
    #
    # search record from 'pattern'  table with current cube's pattern.
    #
    def pattern_search(self, opt = 2):
        pos_data = ''
        col_data = ''
        for cube in self.cube2:
            pos_data += self.convPos2(cube.getPos())
            col_data += self.convCol(cube.getConf())
        cube2_attr=(pos_data, col_data)
        #
        pos_data = ''
        col_data = ''
        for cube in self.cube3:
            pos_data += self.convPos3(cube.getPos())
            col_data += self.convCol(cube.getConf())
        cube3_attr=(pos_data, col_data)
        #
        pt_id = self.db.search_pattern(cube2_attr, cube3_attr)
        if pt_id == None:
            if opt > 1:
                self.cli.prompt(f">現在のパターンに一致するデータは見つかりませんでした。")
        else:
            if opt > 0:
                self.cli.prompt(f">現在のパターンに一致するデータが見つかりました。[pt_id={pt_id}]")
        return pt_id
    #
    # search record from 'pattern'  table by pt_id and view rubik-cubes.
    #
    def pattern_view(self, pt_id):
        if pt_id == 'q':
            self.cli.prompt(f">")
            self.pattern_viewing = False
            return
        if pt_id == 'n' or pt_id == '':
            pt_id, cube2, cube3 = self.db.next_pattern()
            if pt_id == None:
                self.pattern_viewing = False
                self.cli.prompt(f">検索が終了しました。")
                return
        else:
            pt_id, cube2, cube3 = self.db.get_pattern(pt_id)
            if pt_id == None:
                self.cli.prompt(f">指定パターンに一致するパターンIDは見つかりませんでした。")
                return

        cube2_attrs = self.convAttr2(cube2[0], cube2[1])
        cube3_attrs = self.convAttr3(cube3[0], cube3[1])
        #
        i = 0
        for cube in self.cube2:
            cube.setPosA(cube2_attrs[i].get('pos'))
            cube.setConf(cube2_attrs[i].get('conf'))
            i += 1
        i = 0
        for cube in self.cube3:
            cube.setPosA(cube3_attrs[i].get('pos'))
            cube.setConf(cube3_attrs[i].get('conf'))
            i += 1
        #
        self.cli.prompt(f">パターンID={pt_id}。（enter:next/q:quit）")
        self.pattern_viewing = True
        return 
    #
    # get solution-command from 'solution' table by pt_id
    #
    def pattern_get(self, params):
        print(f"pattern_get:{params}")
        if len(params) == 1:
            pt_id = self.pattern_search()
            if pt_id == None:
                return
        else:
            pt_id = params[1]
        cmd,  sl_no = self.db.get_solution(pt_id)
        if cmd == None:
           self.cli.prompt(f">指定パターンの解法は見つかりませんでした。")
        else:
           if len(self.cmdBuffer) > 0:
                self.ope_mode[0] = RubikGame.PLAY_MODE
                self.confirm()
                self.ope_mode[0] = RubikGame.SET_MODE
           self.cli.prompt(f">指定パターンの解法を操作ログに表示します。[pt_id={pt_id},sl_no={sl_no}]")
           self.cmdBuffer.append(cmd.upper())
           cmdline = '操作ログ：'
           cmdline += cmd.upper()
           self.cmdline.setText(cmdline)
        return
    # end of the definition of RubikGame-Class
#
# Main process
#
game = RubikGame()
game.run()
