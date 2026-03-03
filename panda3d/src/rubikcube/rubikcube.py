
from panda3d.core import Material

class RubikCube():
    count = 1       # id:: {type}{count:02}
    type = ''       # '1':center,'2':edge, '3':corner
    # pair face symbol
    face_sym =  ['s', 'n', 'e', 'w', 't', 'b']
    face_pair = ['n', 's', 'w', 'e', 'b', 't']
    # color number:Y/R/G/W/O/B(not used)
    color_num  = (1, 2, 3, 4, 5, 6)
    # against color number(not used)
    color_pair = (4, 5, 6, 1, 2, 3)
    # configuration of color(T/W/S)
    conf_list = [(1, 2, 3), (1, 6, 2), (1, 5, 6), (1, 3, 5),
                 (2, 1, 6), (2, 6, 4), (2, 4, 3), (2, 3, 1),
                 (3, 1, 2), (3, 2, 4), (3, 4, 5), (3, 5, 1),
                 (4, 2, 6), (4, 6, 5), (4, 5, 3), (4, 3, 2),
                 (5, 1, 3), (5, 3, 4), (5, 4, 6), (5, 6, 1),
                 (6, 1, 5), (6, 5, 4), (6, 4, 2), (6, 2, 1),
                 ]
    # list of HPR-values versus conf_list
    hpr_list = [
        (0,    0,   0), (90,   0,  0), (180,  0,   0), (-90,  0,   0),
        (180,  0,  90), (90,   0, 90), (0,    0,  90), (-90,  0,  90),
        (90, -90,   0), (0,   -90, 0), (-90, -90,  0), (-180, -90, 0),
        (0,  180,   0), (-90, 180, 0), (-180, 180, 0), (90, 180,   0),
        (0,    0, -90), (-90,  0,-90), (-180, 0, -90), (90,   0, -90),
        (-90, 90,   0), (-180, 90, 0), (90,  90,   0), (0,   90,   0),
        ] 
    #
    #   base:ShowBase
    #   type:'1':center,'2':edge, '3':corner
    #   mpath: path of model file(RubikCube.egg.pz)
    #
    def __init__(self, base, type, sym, mpath, light = None):
        if type == RubikCube.type:
            RubikCube.count += 1
        else:
            RubikCube.count = 1
        RubikCube.type = type
        #
        self.id = RubikCube.count
        self.type = type
        self.sym = sym
        # current color-configration(T/W/S)
        self.conf = [1, 2, 3]
        #
        # load model(RGB/WYO-Cube) from egg file
        #
        self.cube = base.loader.loadModel(mpath)
        self.cube.reparentTo(base.render)
        self.cube.setScale(1, 1, 1)
        #
        if light != None:
            m = Material()
            #m.setDiffuse((0, 0, 1, 1))
            m.setSpecular((1, 1, 1, 1))
            m.setShininess(128)
            self.cube.setMaterial(m, 1)
            self.cube.setLight(light)

    #
    def getId(self):
        return f"{self.type}{self.id:02}"
    #
    def getPos(self):
        return (self.getX(), self.getY(), self.getZ())
    #
    def setPos(self, x, y, z):
        self.cube.setPos(x, y, z)
    #
    def setPosA(self, pos):
        self.cube.setPos(pos[0], pos[1], pos[2])
    #
    def setHpr(self, h, p, r):
        self.cube.setHpr(h, p, r)
    #
    def getX(self):
        return self.cube.getX()
    #
    def getY(self):
        return self.cube.getY()
    #
    def getZ(self):
        return self.cube.getZ()
    #
    def setX(self, x):
        self.cube.setX(x)
    #
    def setY(self, y):
        self.cube.setY(y)
    #
    def setZ(self, z):
        self.cube.setZ(z)
    #
    def getHpr(self):
        return self.cube.getHpr()
    #
    def setH(self, h):
        self.cube.setH(h)
    #
    def setP(self, p):
        self.cube.setP(p)
    #
    def setR(self, r):
        self.cube.setR(r)
    #
    # set color-configration from Headding
    #
    def setDirH(self, h):
        #print(f"setDirH:{h}")
        #print(f"conf(b):{self.conf}")
        if h < 0:
            ws = self.nextColor((0, self.conf[0]), (1, self.conf[2]), 2)
            self.conf[1] = self.conf[2]
            self.conf[2] = ws
        else:
            ws = self.nextColor((0, self.conf[0]), (2, self.conf[1]), 1)
            self.conf[2] = self.conf[1]
            self.conf[1] = ws
        #
        #print(f"conf(a):{self.conf}")
        #
        return self.setConf2Hpr()
    #
    # set color-configration from Pitch
    #
    def setDirP(self, p):
        #print(f"setDirP:{p}")
        #print(f"conf(b):{self.conf}")
        if p > 0:
            ws = self.nextColor((1, self.conf[1]), (2, self.conf[0]), 0)
            self.conf[2] = self.conf[0]
            self.conf[0] = ws
        else:
            ws = self.nextColor((1, self.conf[1]), (0, self.conf[2]), 2)
            self.conf[0] = self.conf[2]
            self.conf[2] = ws
        #
        #print(f"conf(a):{self.conf}")
        #
        return self.setConf2Hpr()
    #
    # set color-configration from Roll
    #
    def setDirR(self, r):
        #print(f"setDirR:{r}")
        #print(f"conf(b):{self.conf}")
        if r > 0:
            ws = self.nextColor((2, self.conf[2]), (0, self.conf[1]), 1)
            self.conf[0] = self.conf[1]
            self.conf[1] = ws
        else:
            ws = self.nextColor((2, self.conf[2]), (1, self.conf[0]), 0)
            self.conf[1] = self.conf[0]
            self.conf[0] = ws
        #
        #print(f"conf(a):{self.conf}")
        #
        return self.setConf2Hpr()
    #
    # get current color-configration
    #
    def getConf(self):
        return (self.conf[0], self.conf[1], self.conf[2])
    #
    #
    # set color-configration and convert to Hpr 
    #
    def setConf(self, conf):
        self.conf[0] = conf[0]
        self.conf[1] = conf[1]
        self.conf[2] = conf[2]
        self.setConf2Hpr()
    # 
    # create the reverced list
    # (*) not used
    #
    def reversedList(self, list):
        rlist = []
        for val in reversed(list):
            rlist.append(val)
        return rlist
    #
    # serch next color number from color-configration table 
    #
    def nextColor(self, base, shift, next_i):
        base_i = base[0]
        shift_i = shift[0]
        color_num = 0
        for conf in RubikCube.conf_list:
            if conf[base_i] == base[1] and conf[shift_i] == shift[1]:
                color_num = conf[next_i]
                break
        return color_num
    #
    # convert the current color-configration to information(H/P/R) of rotate  
    #
    def setConf2Hpr(self):
        # search the current conf in conf_list
        conf = (self.conf[0],self.conf[1],self.conf[2])
        #print(f"conf:{self.conf}")
        i = self.conf_list.index(conf)
        # get HPR versus color-configration 
        hpr = self.hpr_list[i]
        #print(f"hpr[{i}]:{hpr}")
        # rotate this cube with HPR
        self.cube.setHpr(hpr[0], hpr[1], hpr[2])
        return
    #
    # rotate cube 180 deg. around the X-axis 
    # and shift the WBS to origin
    #
    def upsideDown(self, unit):
        self.setZ( ((-1)*self.getZ() + unit*2) )
        self.setY( ((-1)*self.getY() + unit*2) )
        conf = self.getConf()
        conf_n = ( self.getPairColor(conf[0]), 
                   conf[1],
                   self.getPairColor(conf[2]) )
        self.setConf(conf_n)
        return
    #
    # rotate cube 90 deg. around the X-axis 
    # and shift the WBS to origin
    #
    def upsideFront(self, unit):
        z = self.getZ()
        self.setZ( self.getY() )
        self.setY( (-1)*z + 2*unit)
        conf = self.getConf()
        conf_n = ( self.getPairColor(conf[2]),
                   conf[1], 
                   conf[0],
                    )
        self.setConf(conf_n)
        return
    #
    # rotate cube 90 deg. around the Y-axis 
    # and shift the WBS to origin
    #
    def upsideLeft(self, unit):
        z = self.getZ()
        self.setZ( self.getX() )
        self.setX( (-1)*z + 2*unit)
        conf = self.getConf()
        conf_n = ( self.getPairColor(conf[1]),
                   conf[0], 
                   conf[2],
                    )
        self.setConf(conf_n)
        return
    #
    # get the color-number of opposite side
    #  
    def getPairColor(self, col):
        i = RubikCube.color_num.index(col)
        return RubikCube.color_pair[i]

    @classmethod
    #
    # get the face-symbol of opposite side
    #  
    def getPairFace(cls, face):
        i = cls.face_sym.index(face)
        return cls.face_pair[i]
    #
#
#       