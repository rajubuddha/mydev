# sys.path.append(r"A:\Raju\Development\RajuDev\gatewayAPI")
import hashlib
import xlrd
from tactic_client_lib import TacticServerStub
import time, datetime

from gateway.pcs import pcs


class GatewayMaster(object):
    def __init__(self, xlspath="", inside=False):

        # =======================================================================
        # self.pcAction = pcs(tUser="admin", tPass="gateway_done", cProject="super4", serURL="172.16.44.1")
        #         self.pcAction = pcs(tUser="gateway_gate", tPass="gateway_gate", cProject="super4", serURL="172.16.42.243")
        #         self.pcAction = pcs(tUser="admin", tPass="vtx3", cProject="admin", serURL="172.16.51.40")
        #         self.pcAction = pcs(tUser="ARTIST_A", tPass="ARTIST_A", cProject="dqe_dlf", serURL="172.16.42.243")
        self.pcAction = pcs(tUser="admin", tPass="gateway@done", cProject="super4", serURL="gateway")
        # self.pcAction = pcs(tUser="admin", tPass="vtx3", cProject="automation_test", serURL="172.16.51.40")
        # =======================================================================
        #         self.pcAction = pcs(tUser="admin", tPass="gateway_done", cProject="super4", serURL="172.16.48.13")
        # self.pcAction = pcs(tUser="admin", tPass="vtx2", cProject="dqe_theme_test_01", serURL="172.16.51.34")

        self.inXlspath = xlspath
        self.ser = self.pcAction.getServer()
        if inside:
            self.ser = TacticServerStub.get()

        if xlspath:
            self.fd = xlrd.open_workbook(xlspath)

        self.project = self.ser.get_project()
        self.proj = self.ser.get_project()

    def addGroups(self, groups=['artist'], accessLevel='medium', extCloumns={}):

        '''
        --------------group creation--------------
        '''
        proj = self.proj
        self.ser.set_project(proj)
        sTyp = "login_group"
        cStyp = "sthpw/%s" % sTyp

        for g in groups:

            g = "%s_%s" % (proj, g)
            gData = {'code': g,
                     'access_rules': u'<rules>\n  <rule group="project" code="%s" access="allow"/>\n  <rule group="link" element="asset_list" project="%s" access="allow"/>\n  <rule group="link" element="asset_type_list" project="%s" access="allow"/>\n</rules>\n' % (
                     proj, proj, proj), "project_code": proj, 'access_level': accessLevel, 'login_group': g}

            for i in extCloumns.keys():
                gData[i] = extCloumns[i]

            self.ser.insert(cStyp, data=gData)

    def addToGroup(self, group="", user="", project=None, remove=False):

        # ---------------including in group-----------

        if project:
            cGrp = '%s_%s' % (project, group)
        else:
            cGrp = group

        ligData = {'login_group': cGrp, 'login': user}
        lig_sTyp = "login_in_group"
        lig_cStyp = "sthpw/%s" % lig_sTyp

        self.chkSObjExistCreate(cStype='sthpw/login_group', cCol='login_group', cCode=cGrp,
                                inData={'login_group': cGrp, 'access_level': 'none'}, printOut=False, create=True,
                                update=False, delete=False)

        if not remove:

            self.chkSObjExistCreate(cStype=lig_cStyp, cCol='login_group', cCode=cGrp, secCol='login', secVal=user,
                                    inData=ligData, create=True, update=False, delete=False, printOut=False)

        else:
            self.chkSObjExistCreate(cStype=lig_cStyp, cCol='login_group', cCode=cGrp, secCol='login', secVal=user,
                                    inData=ligData, create=False, update=False, delete=True, printOut=True)

    def chkSObjExistReturn(self, cStype="sthpw/login", cCol="code", cCode=""):

        exp = "@SOBJECT(%s['%s','%s'])" % (cStype, cCol, cCode)
        res = self.ser.eval(exp)

        if len(res):

            return [True, res]
        else:
            return [False]

    def chkSObjExist(self, cStype="sthpw/login", cCol="code", cCode=""):

        exp = "@SOBJECT(%s['%s','%s'])" % (cStype, cCol, cCode)
        res = self.ser.eval(exp)

        if len(res):

            return True
        else:
            return False

    def chkSObjExistCreate(self, cStype="sthpw/login", cCol="code", cCode="", secCol="", secVal="", inData={},
                           printOut=False, create=True, update=False, delete=False):

        if secCol:

            exp = "@SOBJECT(%s['%s','%s']['%s','%s'])" % (cStype, cCol, cCode, secCol, secVal)



        else:

            exp = "@SOBJECT(%s['%s','%s'])" % (cStype, cCol, cCode)

        try:
            res = self.ser.eval(exp)
        except:
            res = []

        if len(res):

            if printOut:
                print ("creation  sType (%s) with name %s skipped" % (cStype, cCode))

            if update:
                self.ser.update(search_key=res[0]['__search_key__'], data=inData)

            if delete:
                self.ser.delete_sobject(search_key=res[0]['__search_key__'], include_dependencies=False)

            return [res[0], True]

        else:

            if create:
                res = self.ser.insert(search_type=cStype, data=inData)
                return [res, False]

    def addUser(self, firstName="", displayName="", loca="", mail="", grd="", hrd="", dept="",
                password=hashlib.md5("DQE@123").hexdigest()):

        # creating users

        sTyp = "login"
        cStyp = "sthpw/%s" % sTyp
        u = firstName
        uData = {'upn': u, 'first_name': u, 'code': u, 'display_name': displayName, 'login': u, 'password': password,
                 'location': loca, 'email': mail, 'grade': grd, 'hr_designation': hrd, 'department': dept}

        try:
            self.chkSObjExistCreate(cStype=cStyp, cCol='code', cCode=u, inData=uData)
        except:

            raise
            print ("create user %s skiped since user exists" % u)

            pass

    def getShotCols(self, shIndx=0, rawCols=[]):

        sh = self.fd.sheet_by_index(shIndx)

        rawDict = {}

        for i in rawCols:
            rawDict[i] = rawCols.index(i)

        readyAdd = True
        inDict = {}

        for n in range(0, sh.ncols):

            if str(sh.row_values(0, 0)[n]).strip() and str(sh.row_values(0, 0)[n]).strip() in rawDict:
                inDict[str(sh.row_values(0, 0)[n]).strip()] = []
                rawDict[str(sh.row_values(0, 0)[n]).strip()] = n

        inSet = set(inDict.keys())
        rawSet = set(rawDict.keys())

        if len(list(rawSet.intersection(inSet))) != len(rawDict.keys()):
            readyAdd = False

        if readyAdd:
            for i in rawDict:

                for q in range(1, sh.nrows):
                    inDict[i].append(sh.row_values(q, 0)[rawDict[i]])
        else:

            print("please check the excel.........")

        return inDict

    def createSeq(self, seqIndex=0, seqStype="sequence", seqInputCols=[], episdeStype='episode'):

        '''

        Creating sequences

        '''

        inDict = self.getShotCols(shIndx=seqIndex, rawCols=seqInputCols)
        seqDict = {}
        self.ser.start("creating sequences............")

        cStype = "%s/%s" % (self.ser.get_project(), seqStype)

        epResDict = self.createEpisode(self, epIndex=0, epStype=episdeStype, epInputCols=seqInputCols)

        '''' updating targets in epsode from episode target sheet..........'''

        # self.updateMultiCoulmns(epTarSheetIndx=4, sType=episdeStype, inCode=epResDict['code'],proj=self.ser.get_project())


        for s in set(inDict['seq']):
            res = self.ser.insert(search_type=cStype, data={"name": s, 'episode_code': epResDict['code']})
            seqDict[s] = res['code']

        self.ser.finish("end of sequence creation............")

        return seqDict

    @staticmethod
    def createEpisode(self, epIndex=0, epStype="episode", epInputCols=[]):

        '''

        Creating episode

        '''
        inDict = self.getShotCols(shIndx=epIndex, rawCols=epInputCols)

        epDict = {}
        self.ser.start("creating episode............")

        cStype_ep = "%s/%s" % (self.ser.get_project(), epStype)

        for s in set(inDict['episode']):

            if self.chkSObjExist(cStype=cStype_ep, cCol='name', cCode=s) == False:
                res = self.ser.insert(search_type=cStype_ep, data={"name": s})

                epDict[s] = res['code']

        self.ser.finish("end of episode creation............")

        return res

    def createShots(self, shtIndx=0, inEpStyp="episode", inSeqSTyp="sequence", inputCols=[], initialTasks=False):

        inDict = self.getShotCols(shIndx=shtIndx, rawCols=inputCols)
        inputCols.append('episode')
        seqDict = self.createSeq(seqIndex=shtIndx, seqStype=inSeqSTyp, seqInputCols=inputCols, episdeStype=inEpStyp)

        cStype = "%s/%s" % (self.ser.get_project(), "shot")

        '''
         Creating Shots

        '''

        self.ser.start("creating shots............")

        shotDict = {}

        cKey = inDict.keys()[0]

        for j in xrange(len(inDict[cKey])):

            inKeys = inDict.keys()

            for k in inKeys:

                if k == "seq":

                    shotDict["sequence_code"] = seqDict[inDict[k][j]]

                elif k == "frames":

                    shotDict["frames"] = int(inDict[k][j])
                else:

                    shotDict[k] = inDict[k][j]

            if len(shotDict) == len(inDict):
                # print shotDict

                self.ser.insert(cStype, data=shotDict)
                if initialTasks:
                    self.initTasks(inTskStype=cStype)

        self.ser.finish("end of shot creation............")

    def addGroupsXls(self, sheetName="Sheet01"):

        self.ser.start(description="Adding groups-------------")
        # self.ser.add_column_to_search_type(search_type="%s/%s" % (self.ser.get_project(), 'sthpw/login_group'), column_name='artist', column_type="Boolean")
        sh = self.fd.sheet_by_name(sheetName)

        for r in range(1, sh.nrows):
            gName = str(sh.row_values(r, 0)[0])
            # self.addGroups(groups=[gName], extCloumns={'artist':int(sh.row_values(r, 0)[1])})
            self.addGroups(groups=[gName])

        self.ser.finish()

    def addUsers(self, inShName="Sheet1", inStartRow=0, inEndRow=200, selOnly=100):

        self.ser.start(description="Adding users-------------")

        inData = self.getDataFromExcelRemap(startRow=inStartRow, endRow=inEndRow, shtName=inShName, getSel=selOnly,
                                            rawCols=['first_name', 'display_name', 'location', 'email', 'grade',
                                                     'hr_designation', 'department'])

        for r in inData:
            fName = self.getDQE_AssociateID(inDict=r, inKey='first_name')

            dName = r['display_name'].strip().upper()

            loc = r['location'].strip().upper()
            e_mail = r['email'].strip().lower()
            a_grd = r['grade'].strip().upper()
            a_hrd = r['hr_designation'].strip().upper()
            dep = r['department'].strip().upper()

            # self.addUser(firstName=fName, displayName=dName)
            fName = str(fName).lower()

            self.addUser(firstName=fName, displayName=dName, loca=loc, mail=e_mail, grd=a_grd, hrd=a_hrd, dept=dep)

        self.ser.finish()

    def createColumnOnStype(self, stype='sthpw/login_group', cColumn=['contentMaker'], cCloumnTyp='boolean'):

        grps = self.ser.query(stype)

        for c in cColumn:

            if len(grps) > 0:

                if 'contentMaker' in grps[0].keys():
                    print "column exists"

            else:
                try:
                    self.ser.add_column_to_search_type(search_type=stype, column_name=c, column_type=cCloumnTyp)
                except:
                    pass

    def addToProjectGroups(self, sheetIndx=1):
        # self.ser.start(description="----Add to group-------------")


        sh = self.fd.sheet_by_index(sheetIndx)

        ''' --------------create groups---------'''

        allDepots = []

        for r in xrange(1, sh.nrows):
            grp = sh.row_values(r, 0)[0]

            grp = grp.lower()
            grp = grp.strip()

            grp = "_".join(grp.split())

            allDepots.append(grp)

        allDepots = list(set(allDepots))
        for cGrp in allDepots:
            print cGrp

            if self.chkSObjExist(cStype="sthpw/login_group", cCol="code", cCode="%s_%s" % (self.project, cGrp)) != True:
                self.addGroups(groups=[cGrp], accessLevel='none')
            else:
                print ("group already exists,creation skiped......")

        '''-------------Add to group-------------'''

        for r in xrange(1, sh.nrows):

            grp = sh.row_values(r, 0)[0]

            grp = grp.lower()
            grp = grp.strip()

            grp = "_".join(grp.split())

            if str(sh.row_values(r, 0)[1]).startswith('P') or str(sh.row_values(r, 0)[1]).startswith('p'):

                member = int(sh.row_values(r, 0)[1][1:])
                member = "P%s" % member

            else:

                member = int(sh.row_values(r, 0)[1])

                '''----------checking the user,group existence,user in group--------'''

            usrChk = self.chkSObjExist(cStype="sthpw/login", cCol="code", cCode=member)

            if usrChk == True:

                exp = "@SOBJECT(sthpw/login_in_group['login','%s']['login_group','%s'])" % (
                member, "%s_%s" % (self.proj, grp))
                resUIG = self.ser.eval(exp)

                if len(resUIG) < 1:

                    self.addToGroup(group=grp, user=member)
                    print "%s added to %s group" % (member, grp)
                else:

                    print "%s already in the %s group" % (member, grp)
                    pass
            else:

                print ("user %s not exists " % member)
                pass

        self.ser.finish()

    def addColumns(self, sType="episode", sheetIndx=4):

        self.ser.start(description="start of add columns to %s-------------" % sType)

        sh = self.fd.sheet_by_index(sheetIndx)

        for r in xrange(1, sh.nrows):
            grp = str(sh.row_values(r, 0)[0])
            self.ser.add_column_to_search_type(search_type="%s/%s" % (self.ser.get_project(), sType), column_name=grp,
                                               column_type="float")

        self.ser.finish("end of add columns to %s-------------" % sType)

    def updateMultiCoulmns(self, epTarSheetIndx=4, sType="episode", proj="", inCode=""):

        self.ser.start(description="start of add columns to %s-------------" % sType)

        sh = self.fd.sheet_by_index(epTarSheetIndx)
        cData = {}

        for r in xrange(1, sh.nrows):
            grp = str(sh.row_values(r, 0)[0])
            val = str(sh.row_values(r, 0)[1])

            cData[grp] = val

        cSType = "%s/%s" % (proj, sType)
        cSkey = self.ser.build_search_key(search_type=cSType, code=inCode)
        self.ser.update(search_key=cSkey, data=cData)

        self.ser.finish("end of add columns to %s-------------" % sType)

    def updateCoulmn(self, epTarSheetIndx=3, sType="episode", proj="", colName=""):

        self.ser.start(description="start of add columns to %s-------------" % sType)

        sh = self.fd.sheet_by_index(epTarSheetIndx)

        for r in xrange(1, sh.nrows):

            val = str(sh.row_values(r, 0)[1])

            if str(sh.row_values(r, 0)[0]).startswith('P') or str(sh.row_values(r, 0)[0]).startswith('p'):

                key = int(sh.row_values(r, 0)[0][1:])
                key = "P%s" % key
            else:

                key = int(sh.row_values(r, 0)[0])

            cSType = "%s/%s" % (proj, sType)

            cSkey = self.ser.build_search_key(search_type=cSType, code=key)

            self.ser.update(search_key=cSkey, data={colName: '%s' % val})

        self.ser.finish("end of add columns to %s-------------" % sType)

    def getUsersFromGrp(self):

        cProj = self.ser.get_project()

        cL_Exp = "@GET(sthpw/login_group['project_code','%s'].sthpw/login_in_group.login)" % cProj
        resL = self.ser.eval(expression=cL_Exp)

        cLG_Exp = "@GET(sthpw/login_group['project_code','%s'].sthpw/login_in_group.login_group)" % cProj
        resG = self.ser.eval(expression=cLG_Exp)

        ugDict = {}
        for i in resL:
            ugDict[i] = resG[resL.index(i)]

        fGL = {}
        for g in resG:

            fGL[g] = []

            for i in resL:

                if ugDict[i] == g:
                    fGL[g].append(i)

        return fGL

    def getAllUsersInProj(self, keyColmun='artist'):

        #         method to get all users in the project except nonWorkingGrps members

        cPGrps = []

        pro = self.ser.get_project()

        for i in self.ser.query('sthpw/login_in_group'):

            if i["login_group"].find(pro) != -1:

                getArtistColExp = "@GET(sthpw/login_group['code','%s'].%s)" % (i['login_group'], keyColmun)

                chkArtGrp = self.ser.eval(getArtistColExp)

                if chkArtGrp[0] == True:
                    cPGrps.append(i["login_group"])

        cPGrps = list(set(cPGrps))
        cPUsrs = []

        for cg in cPGrps:
            cPUsrs = self.getUsersFromGrp()[cg] + cPUsrs

        return cPUsrs

    def changePassword(self, inPass=""):

        self.ser.eval(
            "@UPDATE(@SOBJECT(sthpw/login['code','$LOGIN']), 'password', '%s')" % hashlib.md5(inPass).hexdigest())

    def createMultiSObjectFromData(self, cStyp="super4_template2/asset_type",
                                   dataVals=['char', 'set', 'prop', 'vehicle', 'fx', 'mgd'], dataKey='name'):

        self.ser.start("----------adding asset types-----------")

        for i in dataVals:

            if self.chkSObjExist(cStype=cStyp, cCol=dataKey, cCode=i) == False:

                self.ser.insert(search_type=cStyp, data={dataKey: i})

            else:

                print (" already exists........ ")

        self.ser.finish()

    def getCodeByName(self, inName, sType=""):

        exp = "@GET(%s['name','%s'].code)" % (sType, inName)
        res = self.ser.eval(exp)

        return res

    def createAssetsFromExcel(self, aType=True, curStype='asset', epStyp='episode', aSType='asset_type', epi=''):

        '''

        create assets from episode assets list excel, every asset type should be separated in diffrent sheets and sheet names shold be strart with asset types

        like below mentioned

        number        type               name

        sheetX--------characters----------char
        sheetX--------CHARACTERS----------char

        sheetX--------sets----------sets
        sheetX--------SETS----------sets

        sheetX--------props----------prop
        sheetX--------PROPS----------prop

        sheetX--------vehicle----------vehi
        sheetX--------VEHICLE----------vehi

        --------------- require stype ---------------------

                epSType   aSType
                    \      /
                     \    /
                      \  /
                       \/
                    curStype

        ---------------------------------------------------



        '''

        allShts = self.fd.sheet_names()

        shts = []

        for i in allShts:
            name = i[0:4].lower()
            shts.append(name)

        '''                adding assets                   '''

        self.ser.start("--------------adding asset types if not available ------------")

        for i in allShts:

            if i[0:4].lower() in shts:

                cShet = i[0:4].lower()

                inExlSht = self.fd.sheet_by_name(i)

                for j in range(1, inExlSht.nrows):

                    name = inExlSht.row_values(j)[0]

                    cData = {'name': name}

                    if epi:
                        epData = self.chkSObjExistCreate(cStype="%s/%s" % (self.proj, epStyp), cCol='name', cCode=epi,
                                                         inData={'name': epi})
                        cData['episode_code'] = epData[0]['code']

                    if aType:
                        aTypeCode = self.chkSObjExistCreate(cStype="%s/%s" % (self.proj, aSType), cCol='name',
                                                            cCode=cShet, inData={'name': cShet})
                        cData['asset_type_code'] = aTypeCode[0]['code']

                    self.chkSObjExistCreate(curStype, cCol='name', cCode=name, inData=cData, startRow=0)

        self.ser.finish()

    def getDataFromExcel(self, rawCols=['sequence', 'shot', 'time in day', 'char', 'vehicles'], shtName=''):

        sh = self.fd.sheet_by_name(shtName)

        rawDict = {}

        for i in rawCols:
            rawDict[i] = rawCols.index(i)

        readyAdd = True
        inDict = {}

        for n in range(0, sh.ncols):

            if str(sh.row_values(0, 0)[n]).strip() and str(sh.row_values(0, 0)[n]).strip() in rawDict:
                inDict[sh.row_values(0, 0)[n].strip()] = []
                rawDict[sh.row_values(0, 0)[n].strip()] = n

        inSet = set(inDict.keys())
        rawSet = set(rawDict.keys())

        if len(list(rawSet.intersection(inSet))) != len(rawDict.keys()):
            readyAdd = False

        if readyAdd:
            for i in rawDict:

                for q in range(1, sh.nrows):
                    inDict[i].append(sh.row_values(q, 0)[rawDict[i]])
        else:

            print("please check the excel columns are not matching.........")

        finData = []

        for k in range(len(inDict[inDict.keys()[0]])):
            outDict = {}
            for j in inDict.keys():
                outDict[j] = inDict[j][k]
            finData.append(outDict)

        return finData

    def feedTBDFixedCols(self, inEp='', shtName='',
                         shotDataCols=['shot', 'frame', 'time in day', 'environment', 'sequence'], startRow=0,
                         assetDataCols=['char', 'props', 'sets', 'vehicles']):

        inExlSht = self.fd.sheet_by_name(shtName)
        self.chkSObjExistCreate(cStype="%s/episode" % self.proj, cCol='name', cCode=inEp, inData={'name': inEp})

        '''                                 shot creation

                                shhotDataCols to limit the input data                 '''

        rawCols = inExlSht.row_values(startRow)

        self.ser.start("----------------- creating shots form a TBD Excel %s --------------------" % self.inXlspath)

        for i in range(1, inExlSht.nrows):

            cData = inExlSht.row_values(i)
            outDict = {}
            for j in cData:

                '''----------------reads only shotDataCols to limit the input data-----------'''

                if rawCols[cData.index(j)] in shotDataCols:

                    if rawCols[cData.index(j)] != "sequence":

                        if rawCols[cData.index(j)] == "shot":

                            outDict['name'] = str(j)
                        elif rawCols[cData.index(j)] == "time in day":

                            outDict["time_in_day"] = str(j)

                        elif rawCols[cData.index(j)] == "frame":

                            outDict[rawCols[cData.index(j)]] = int(j)

                        else:

                            outDict[rawCols[cData.index(j)]] = str(j)

                    else:

                        cEpCode = self.getCodeByName(inName=inEp, sType="%s/episode" % self.proj)[0]
                        res = self.chkSObjExistCreate(cStype="%s/sequence" % self.proj, cCol='name', cCode=str(j),
                                                      secCol='episode_code', secVal=cEpCode,
                                                      inData={'name': str(j), 'episode_code': cEpCode})
                        outDict["sequence_code"] = res[0]['code']

            self.chkSObjExistCreate(cStype="%s/shot" % self.proj, cCol='name', cCode=outDict['name'], inData=outDict)

        '''                         asset in shot creation                         '''

        keyCol = "shot"

        rawCols = inExlSht.row_values(0)

        for i in range(1, inExlSht.nrows):

            cData = inExlSht.row_values(i)

            for j in cData:

                if rawCols[cData.index(j)] == keyCol:
                    cShot = str(j)

                if rawCols[cData.index(j)] in assetDataCols:

                    for k in j.split():
                        outDict = {}
                        cAsset = k.strip().lower()
                        cAsset_code = self.getCodeByName(inName=cAsset, sType="%s/asset" % self.proj)[0]
                        exp = "@GET(%s/asset['code','%s'].asset_type_code)" % (self.proj, cAsset_code)
                        asType_code = self.ser.eval(exp)[0]
                        exp = "@GET(%s/asset_type['code','%s'].name)" % (self.proj, asType_code)
                        asType_name = self.ser.eval(exp)[0]

                        cShot_code = self.getCodeByName(inName=cShot, sType="%s/shot" % self.proj)[0]
                        outDict['shot_code'] = cShot_code
                        outDict['name'] = cAsset
                        outDict['asset_code'] = cAsset_code

                        # print outDict
                        print outDict
                        self.ser.insert(search_type="%s/%s_in_shot" % (self.proj, asType_name), data=outDict)

                        outDict['asset_type_code'] = asType_code

                        ''' can be disable if asset in shot required '''
                        self.ser.insert(search_type="%s/asset_in_shot" % self.proj, data=outDict)

        self.ser.finish(
            "----------------- End of the shot creation form TBD Excel %s --------------------" % self.inXlspath)

    def feedTBD(self, inEp='', inShtName='', shotDataCols=['shot', 'frame', 'time in day', 'environment', 'sequence'],
                startRow=0, assetDataCols=['char', 'props', 'sets', 'vehicles'], keyCol='shot', shotStype='shot'):

        self.ser.start("----------------- creating shots form a TBD Excel %s --------------------" % self.inXlspath)

        shotData = self.getDataFromExcel(rawCols=shotDataCols, shtName=inShtName)

        for i in shotData:

            cDict = {}

            for j in i.keys():

                if j != "sequence":

                    if j == keyCol:

                        cDict['name'] = i[j]

                    elif j == 'time in day':

                        cDict['time_in_day'] = i[j]
                    elif j == 'frame':

                        try:
                            cDict['frame'] = int(i[j])
                        except:

                            cDict['frame'] = 0
                else:
                    cDict[j] = i[j]
                    cEpCode = self.getCodeByName(inName=inEp, sType="%s/episode" % self.proj)[0]
                    res = self.chkSObjExistCreate(cStype="%s/sequence" % self.proj, cCol='name', cCode=i[j],
                                                  secCol='episode_code', secVal=cEpCode,
                                                  inData={'name': i[j], 'episode_code': cEpCode})
                    cDict["sequence_code"] = res[0]['code']

                    cDict.pop('sequence')

            self.chkSObjExistCreate(cStype="%s/%s" % (self.proj, shotStype), cCol='name', cCode=cDict['name'],
                                    inData=cDict)
            print cDict

        '''                         asset in shot creation                         '''

        keyCol = "shot"

        assetDataCols.append(keyCol)
        assetsData = self.getDataFromExcel(rawCols=assetDataCols, shtName=inShtName)

        for i in assetsData:

            cShot = i[keyCol]
            for a in i.keys():

                if a in assetDataCols and a != keyCol:

                    for k in i[a].split():
                        outDict = {}
                        cAsset = k.strip().lower()

                        cAsset_code = self.getCodeByName(inName=cAsset, sType="%s/asset" % self.proj)[0]
                        exp = "@GET(%s/asset['code','%s'].asset_type_code)" % (self.proj, cAsset_code)
                        asType_code = self.ser.eval(exp)[0]
                        exp = "@GET(%s/asset_type['code','%s'].name)" % (self.proj, asType_code)
                        asType_name = self.ser.eval(exp)[0]

                        cShot_code = self.getCodeByName(inName=cShot, sType="%s/shot" % self.proj)[0]
                        outDict['shot_code'] = cShot_code
                        outDict['name'] = cAsset
                        outDict['asset_code'] = cAsset_code

                        # print outDict
                        self.ser.insert(search_type="%s/%s_in_shot" % (self.proj, asType_name), data=outDict)

                        outDict['asset_type_code'] = asType_code

                        '''
                            can be disable if asset in shot required

                        '''
                        self.ser.insert(search_type="%s/asset_in_shot" % self.proj, data=outDict)

        self.ser.finish(
            "----------------- End of the shot creation form TBD Excel %s --------------------" % self.inXlspath)

    def fillArray(self, one=[1, 2, 3, 4, 5], two=[1, 1]):
        oLen = len(two)
        if len(two) != len(one):
            while len(two) < len(one):
                if oLen == 0:
                    two = one
                else:
                    two.append(one[oLen])
                oLen += 1

        return two

    def getDataFromExcelRemap(self, startRow=0, endRow=100, getSel=0,
                              rawCols=['sequence', 'shot', 'time in day', 'char', 'vehicles'], shtName='', remap=[],
                              bCrop=[None, None, None, None, None], fCrop=[None, None, None, None, None]):

        remap = self.fillArray(one=rawCols, two=remap)
        sh = self.fd.sheet_by_name(shtName)
        rawDict = {}

        for i in rawCols:
            rawDict[i] = rawCols.index(i)

        readyAdd = True
        inDict = {}

        for n in range(0, sh.ncols):

            try:
                cValue = sh.row_values(startRow, 0)[n].strip()

            except:

                cValue = sh.row_values(startRow, 0)[n]

            if cValue and cValue in rawDict:
                inDict[sh.row_values(startRow, 0)[n].strip()] = []
                rawDict[sh.row_values(startRow, 0)[n].strip()] = n

        inSet = set(inDict.keys())
        rawSet = set(rawDict.keys())

        if len(list(rawSet.intersection(inSet))) != len(rawDict.keys()):
            readyAdd = False

        if readyAdd:
            for i in rawDict:

                for q in range(1, endRow):
                    inDict[i].append(sh.row_values(q, 0)[rawDict[i]])
        else:

            print("please check the excel columns are not matching.........")

        finData = []

        for k in range(len(inDict[inDict.keys()[0]])):
            outDict = {}
            kys = inDict.keys()
            for j in kys:
                try:
                    outDict[remap[rawCols.index(j)]] = inDict[j][k][fCrop[rawCols.index(j)]:bCrop[rawCols.index(j)]]
                except:
                    outDict[remap[rawCols.index(j)]] = inDict[j][k]

            finData.append(outDict)

        if getSel:
            return [finData[getSel - 2]]

        return finData[startRow:]

    def splitChkGetCode(self, inStr="", splitCode='\n', sType='', chkCol='name'):

        cSets = inStr.split(splitCode)
        outNEs = []
        outEs = []
        outEsCode = []
        for j in cSets:

            if j.lower() and a.chkSObjExist(cStype=sType, cCol=chkCol, cCode=j.lower()) == False:

                outNEs.append(j)

            elif j.lower():

                exp = "@GET(%s['%s','%s'].code)" % (sType, chkCol, j.lower())

                eCode = a.ser.eval(exp)[0]
                outEsCode.append(eCode)
                outEs.append(j.lower())

        return {'exists': outEs, 'existsCode': outEsCode, 'notExists': outNEs}

    def makeShotsExcel(self, cEp='202', SheetName='', iStartRow=7, iEndRow=210,
                       iRawCols=['Shot', 'Shot duration (frames)', 'time in day', 'INT EXT', 'sequence', 'COMMENTS'],
                       iRemap=['name', 'frame', 'time_in_day', 'environment', 'sequence_code', 'description']):

        self.ser.start(description='--------tbd feed-----------')
        epRes = self.chkSObjExistCreate(cStype="%s/episode" % self.proj, cCol='name', cCode=cEp, inData={"name": cEp})

        for i in self.getDataFromExcelRemap(startRow=iStartRow, endRow=iEndRow, rawCols=iRawCols, shtName=SheetName,
                                            remap=iRemap):

            try:
                cFrame = int(i['frame'])
            except:
                cFrame = 0

            seqRes = self.chkSObjExistCreate(cStype='%s/sequence' % self.proj, cCol='name', cCode=i['sequence_code'],
                                             secCol='episode_code', secVal=epRes[0]['code'],
                                             inData={'name': i['sequence_code'], 'episode_code': epRes[0]['code']})
            i['sequence_code'] = seqRes[0]['code']
            self.chkSObjExistCreate(cStype='%s/shot' % self.proj, cCol='name', cCode=i['name'], secCol='episode_code',
                                    secVal=epRes[0]['code'],
                                    inData={"name": i['name'], 'frame': cFrame, "time_in_day": i['time_in_day'],
                                            'environment': i['environment'], 'sequence_code': i['sequence_code'],
                                            'description': i['description'], 'episode_code': epRes[0]['code'],
                                            'ep_num': cEp})

        self.ser.finish()

    def addAssetsToShots(self, cEp='202', SheetName='', splitChar='\n', iStartRow=0, iEndRow=200, nameMapOutDict={},
                         iRawCols=['Shot', 'SET', 'CHARACTERS', 'VEHICLES', 'PROPS', 'VFX'],
                         iRemapCols=['name', 'SET', 'CHARACTERS', 'VEHICLES', 'PROPS', 'VFX'],
                         allAssetCols=['SET', 'CHARACTERS', 'VEHICLES', 'PROPS', 'VFX'],
                         sTypeDict={'SET': '$PROJECT/sets_in_shot', 'CHARACTERS': '$PROJECT/char_in_shot',
                                    'VEHICLES': '$PROJECT/vehi_in_shot', 'PROPS': '$PROJECT/prop_in_shot',
                                    'VFX': '$PROJECT/vfx_in_shot'}):

        for m in allAssetCols:

            self.ser.start('--------tbd feed-----------')

            epRes = self.chkSObjExistCreate(cStype="%s/episode" % self.proj, cCol='name', cCode=cEp,
                                            inData={"name": cEp})
            for i in self.getDataFromExcelRemap(startRow=iStartRow, endRow=iEndRow, rawCols=iRawCols, remap=iRemapCols,
                                                shtName=SheetName):

                shtRes = self.chkSObjExistCreate(cStype='%s/shot' % self.proj, cCol='name', cCode=i['name'],
                                                 secCol='episode_code', secVal=epRes[0]['code'],
                                                 inData={'name': i['name'],
                                                         'description': 'created while adding assets to the shot since shot was not created'})
                shtCode = shtRes[0]['code']

                if i[m]:

                    for j in i[m].split(splitChar):

                        if j:

                            try:

                                cAsset = nameMapOutDict[j.strip().split()[0]]

                            except:

                                cAsset = "asset not found"
                            aStatus = self.chkSObjExist(cStype='%s/asset' % self.proj, cCol='name', cCode=cAsset)
                            if aStatus == False:
                                try:
                                    print j.strip().split()[0], "----------------", aStatus

                                except:
                                    pass

                            else:
                                aCode = self.getCodeByName(inName=cAsset, sType='%s/asset' % self.proj)[0]
                                self.chkSObjExistCreate(cStype=sTypeDict[m], cCol='asset_code', cCode=aCode,
                                                        secCol='shot_code', secVal=shtCode,
                                                        inData={'name': cAsset, 'asset_code': aCode,
                                                                'shot_code': shtCode}, printOut=True)
            self.ser.finish()

    def makeTasksFromPanel(self, cEp='', sType='shot', psType='', noPts=['render', 'render QC', 'comp', 'edit', 'fur'],
                           sShot=None, eShot=None, allPipe=True, inProcesses=['']):

        cEp_code = self.getCodeByName(inName=cEp, sType="%s/episode" % self.proj)[0]
        actProcesses = {'blocking': 'anim', 'secondary': 'anim', 'lighting': 'lit', 'fx': 'fx', 'comp': 'comp',
                        'layout': 'layout', 'lip_sync': 'lip_sync', 'fur_sim': 'fur_sim', 'hair_sim': 'hair_sim',
                        'edit': 'edit', 'render': 'render', 'render_chk': 'render_chk'}

        self.ser.start(description="panel based tasks creation start")

        for i in self.ser.eval("@SOBJECT($PROJECT/%s['episode_code','%s'])" % (sType, cEp_code)):

            iPanel = self.ser.eval("@SOBJECT($PROJECT/%s['code','%s'])" % (psType, i['%s_code' % psType]))[0]

            if allPipe:
                allProcesses = self.ser.get_pipeline_processes(search_key=i['__search_key__'])
            else:
                allProcesses = inProcesses

            for p in allProcesses:

                if p not in noPts:

                    if (iPanel[actProcesses[p]] > 0):
                        print p, iPanel[actProcesses[p]]

                        if p == 'lighting':

                            self.ser.add_initial_tasks(search_key=i['__search_key__'],
                                                       processes=[p, 'render', 'render_chk'], skip_duplicate=True)
                        else:
                            self.ser.add_initial_tasks(search_key=i['__search_key__'], processes=[p],
                                                       skip_duplicate=True)

        self.ser.finish(description="panel based tasks creation end")

    def makeDQE_ProjectStypes(self, sTypesList=['shot', 'asset', 'panel_shot', 'panel_asset', 'episode', 'char_in_shot',
                                                'fur_in_shot', 'sets_in_shot', 'prop_in_shot', 'vehi_in_shot',
                                                'vfx_in_shot', 'mgd_in_shot', 'client_input', "split_asset",
                                                "split_shot", 'sequence', 'review_shot', 'review_asset', 'asset_type',
                                                'cam_move', 'shot_type', 'widget_settings', 'client_feedback',
                                                'workarea', 'pc_master_log', 'status_report', 'report_processes',
                                                'status_report_parcentage', 'pyd', 'client_review'], rCols={
        'panel_asset': ['model', 'unwrap', 'texturing', 'facial', 'set dressing', "master lighting", 'fx', 'hair',
                        'fur', 'asset_comp', "rigging"],
        'panel_shot': ['layout', 'lip sync', 'anim', 'fx', 'hair sim', 'cloth sim', 'lit', 'render', 'fur sim', 'comp'],
        'shot': ['time_in_day', 'environment', 'frame'], 'asset': ['season', 'MP_epi', 'base_episode'],
        'pc_master_log': ['action', 'action_msg']}, rColsDT={
        'panel_asset': ['float', 'float', 'float', 'float', 'float', "float", 'float', 'float', 'float', 'float',
                        "float"],
        'panel_shot': ['float', 'float', 'float', 'float', 'float', 'float', 'float', 'float', 'float', 'float'],
        'shot': ['text', 'text', 'text'], 'asset': ['text', 'text', 'text'], 'pc_master_log': ['text', 'text']}):

        for i in sTypesList:

            try:
                self.ser.create_search_type(search_type=i, title=i)
            except:

                print "stype creation skipped %s" % i

            print i

            try:
                cProj = self.proj
                cCols = rCols[i]
                cTypes = rColsDT[i]

                for j in rCols[i]:
                    print "-----------------------------" + j + "-----------------" + rColsDT[i][rCols[i].index(j)]
                    self.ser.add_column_to_search_type(search_type="%s/%s" % (cProj, i), column_name=j,
                                                       column_type=cTypes[cCols.index(j)])
            except:

                pass

        '''--------------------------------------make sequence code---------------------------'''

        for i in ['shot', 'panel_shot']:
            self.ser.add_column_to_search_type(search_type="%s/%s" % (i, cProj), column_name='sequence_code',
                                               column_type='varchar')

        '''--------------------------------------make episode code---------------------------'''

        for i in ['shot', 'asset', 'panel_asset', 'panel_shot', 'sequence', 'widget_settings', 'status_report',
                  'status_report_parcentage', 'client_feedback']:
            self.ser.add_column_to_search_type(search_type="%s/%s" % (i, cProj), column_name='episode_code',
                                               column_type='varchar')

        '''--------------------------------------make shot code---------------------------'''

        for i in ['char_in_shot', 'fur_in_shot', 'sets_in_shot', 'prop_in_shot', 'vehi_in_shot', 'vfx_in_shot',
                  "split_shot", 'review_shot']:
            self.ser.add_column_to_search_type(search_type="%s/%s" % (i, cProj), column_name='shot_code',
                                               column_type='varchar')

        '''--------------------------------------make asset code---------------------------'''

        for i in ['char_in_shot', 'fur_in_shot', 'sets_in_shot', 'prop_in_shot', 'vehi_in_shot', 'vfx_in_shot',
                  "split_asset", 'review_asset']:
            self.ser.add_column_to_search_type(search_type="%s/%s" % (i, cProj), column_name='asset_code',
                                               column_type='varchar')

        '''--------------------------------------make shot input code---------------------------'''

        for i in ['shot']:
            self.ser.add_column_to_search_type(search_type="%s/%s" % (i, cProj), column_name='panel_shot_code',
                                               column_type='varchar')
            self.ser.add_column_to_search_type(search_type="%s/%s" % (i, cProj), column_name='sequence_code',
                                               column_type='varchar')
            self.ser.add_column_to_search_type(search_type="%s/%s" % (i, cProj), column_name='shot_type_code',
                                               column_type='varchar')
            self.ser.add_column_to_search_type(search_type="%s/%s" % (i, cProj), column_name='cam_move_code',
                                               column_type='varchar')

        '''--------------------------------------make pyd code---------------------------'''

        for i in ['panel_asset', 'panel_shot', 'client_input']:
            self.ser.add_column_to_search_type(search_type="%s/%s" % (i, cProj), column_name='pyd_code',
                                               column_type='varchar')

        '''--------------------------------------make pyd code---------------------------'''

        for i in ['panel_asset', 'pyd', 'asset']:
            self.ser.add_column_to_search_type(search_type="%s/%s" % (i, cProj), column_name='asset_type_code',
                                               column_type='varchar')

        '''----------------------------------------------report processes code---------------------------------------------'''

        for i in ['status_report_parcentage', 'status_report']:
            self.ser.add_column_to_search_type(search_type="%s/%s" % (i, cProj), column_name='report_processes_code',
                                               column_type='varchar')

        '''----------------------------------------------panel asset code---------------------------------------------'''

        for i in ['asset']:
            self.ser.add_column_to_search_type(search_type="%s/%s" % (i, cProj), column_name='panel_asset_code',
                                               column_type='varchar')

    def cleanProjectStypes(self):

        for i in self.ser.query(search_type='sthpw/search_type'):

            test = i['code']

            if test.find('%s/' % self.proj) != -1 and self.proj != 'admin':
                self.ser.delete_sobject(search_key=i['__search_key__'])
                print (i)

    def makeGroupsFromProcesses(self, inStype="shot"):

        self.ser.start(description="make groups from processes start")
        '''

        at least one sobject is required to query pipeline process

        '''

        for i in self.ser.query('%s/%s' % (self.proj, inStype))[0:1]:

            resProcs = self.ser.get_pipeline_processes(search_key=i['__search_key__'])

            for j in resProcs:
                print "%s_%s" % (self.proj, j)

                sTyp = "login_group"
                cStyp = "sthpw/%s" % sTyp
                g = "%s_%s" % (self.proj, j)
                gData = {'code': g,
                         'access_rules': u'<rules>\n  <rule group="project" code="%s" access="allow"/>\n  <rule group="link" element="asset_list" project="%s" access="allow"/>\n  <rule group="link" element="asset_type_list" project="%s" access="allow"/>\n</rules>\n' % (
                         self.proj, self.proj, self.proj), "project_code": self.proj, 'access_level': u'low',
                         'login_group': g}

                self.chkSObjExistCreate(cStype=cStyp, cCol='code', cCode=g, inData=gData)

        self.ser.finish(description="make groups from processes end")

    def addToProjectGrpExcel(self, SheetName='', iStartRow=0, iEndRow=100, iRawCols=['first_name', 'department'],
                             iRemap=['login', 'group'],
                             noGrp=['Direction', 'Production_Management', 'Production_Tracking']):

        actGrpMap = {'VFX': 'fx', 'Comp': 'comp', 'Lighting': 'lighting', 'Animation': 'blocking',
                     'Lipsync': 'lip_sync', 'Layout': 'layout', 'Modeling': 'modeling', 'Texturing': 'texturing',
                     'Fur': 'fur',
                     'Rigging': 'rigging', 'Set Dressing': 'set_dressing', 'Master_Lighting': 'master_lighting',
                     'Facial': 'facial', 'Asset_Comp': 'asset_comp', 'hair_sim': 'hair_sim', 'cloth_sim': 'cloth_sim',
                     'fur_sim': 'fur_sim', 'Render': 'render', 'Edit': 'edit'
                     }

        for u in self.getDataFromExcelRemap(startRow=iStartRow, endRow=iEndRow, rawCols=iRawCols, shtName=SheetName,
                                            remap=iRemap):

            cG = u['group'].split()
            u['group'] = "_".join(cG)

            if u['group'] not in noGrp:

                cUser = str(u['login']).lower().split(".")[0]
                cGrp = u'%s_%s' % (self.proj, actGrpMap[u['group']])
                if self.chkSObjExist(cStype='sthpw/login', cCol='login', cCode=cUser):
                    self.chkSObjExistCreate(cStype='sthpw/login_in_group', cCol='login_group', cCode=cGrp,
                                            secCol='login', secVal=cUser, inData={'login_group': cGrp, 'login': cUser},
                                            printOut=True)

    def makeGroups(self, groups=['artist'], accessLevel='medium', xmlRule="<rules></rules>"):

        '''
        --------------group creation--------------
        '''
        proj = self.proj
        self.ser.set_project(proj)
        sTyp = "login_group"
        cStyp = "sthpw/%s" % sTyp

        for g in groups:
            g = "%s_%s" % (proj, g)
            gData = {'code': g, 'access_level': accessLevel, 'login_group': g, 'access_rules': xmlRule}

            self.ser.insert(cStyp, data=gData)

    def status_update(self, sKey="", outProcess='blocking', outStatus="Pending", sType='shot'):

        cCode = sKey.split("=")[-1]
        prnt = self.ser.eval("@GET(sthpw/task['code','%s'].parent.code)" % cCode)[0]
        prntTask = \
        self.ser.eval("@GET($PROJECT/%s['code','%s'].sthpw/task['process','%s'].code)" % (sType, prnt, outProcess))[0]
        self.ser.eval("@UPDATE(@SOBJECT(sthpw/task['code','%s']),'status','%s')" % (prntTask, outStatus))

    def make_task_in_trigger(self, inSkey="", newProcess="lighting",
                             newTaskData={'status': 'Pending', 'supervisor': ''}):

        sKey = inSkey
        cCode = sKey.split("=")[-1]

        psrt = a.ser.eval("@GET(sthpw/task['code','%s'].search_type)" % cCode[0])[0]
        psc = a.ser.eval("@GET(sthpw/task['code','%s'].search_code)" % cCode[0])[0]
        pst = psrt.split("?")[0]
        shObj = a.ser.eval("@SOBJECT(%s['code','%s'])" % (pst, psc))[0]
        newTaskData['episode'] = shObj['ep_num']
        res = a.ser.add_initial_tasks(search_key=shObj["__search_key__"], pipeline_code=pst, processes=[newProcess],
                                      skip_duplicate=True)[0]
        a.ser.update(search_key=res['__search_key__'], data=newTaskData)

    def supervisorApp(self, inSkey=""):

        sKey = inSkey

        cCode = sKey.split("=")[-1]
        proj = self.ser.eval("$PROJECT")
        prntTask = self.ser.eval("@GET(sthpw/task['code','%s'].parent.org_task)" % cCode)
        cTask = self.ser.eval("@SOBJECT(sthpw/task['code','%s'])" % cCode)[0]

        # ------------------------------- Approve Take Increments ------------------------------

        cTk = self.ser.eval("@GET(sthpw/task['code','%s'].e_count)" % cCode)[0]

        nTkVal = int(cTk) + 1

        nTkTx = "E-Take{:02d}".format(nTkVal)

        self.ser.update(search_key=prntTask, data={'status': "I_App", 'take': nTkTx})
        self.ser.update(search_key=prntTask, data={'e_count': nTkVal})

        prntCode = prntTask[0].split('=')[-1]

        oProcess = self.ser.eval("@GET(sthpw/task['code','%s'].process)" % prntCode)
        oAssign = self.ser.eval("@GET(sthpw/task['code','%s'].assigned)" % prntCode)
        cPanel = self.ser.eval(
            "@GET(sthpw/task['code','%s'].%s/shot.%s/panel_shot.%s)" % (prntCode, proj, proj, oProcess[0]))

        self.ser.insert("sthpw/associate_productivity", data={'complexity': cPanel, 'login': oAssign[0]})
        cTaskProcs = self.ser.eval("@GET(sthpw/task['code','%s'].process)" % prntCode)
        cLogin = self.ser.eval('$LOGIN')
        pStype = self.ser.eval("@GET(sthpw/task['code','%s'].search_type)" % prntCode)
        cMsg = cTask['supervisor_comment']
        pSCode = self.ser.eval("@GET(sthpw/task['code','%s'].parent.code)" % prntCode)
        nData = {'note': cMsg, 'search_type': pStype, 'search_code': pSCode, 'process': cTaskProcs, 'login': cLogin,
                 'context': cTaskProcs}

        self.ser.insert('sthpw/note', data=nData)

        # ------------------------------- Create Client review task ------------------------------

        prnt = self.ser.eval("@SOBJECT(sthpw/task['code','%s'].parent)" % cCode)[0]
        desc = "created for %s's %s process" % (prnt['name'], cTask['process'])

        resT = self.ser.create_task(search_key=prnt['__search_key__'], process="clent_review", description=desc,
                                    assigned='admin')
        self.ser.update(search_key=resT['__search_key__'],
                        data={'take': nTkTx, 'status': 'Assignment', 'i_count': cTask['i_count'], 'e_count': nTkVal})

    def supervisorRject(self):

        # -------------------------------Supervisor Reject------------------------------

        sKey = input.get("search_key")
        cCode = sKey.split("=")[-1]
        prntTask = self.ser.eval("@GET(sthpw/task['code','%s'].parent.org_task)" % cCode)
        prntCode = prntTask[0].split('=')[-1]
        cTask = self.ser.eval("@SOBJECT(sthpw/task['code','%s'])" % cCode)[0]

        cTaskProcs = self.ser.eval("@GET(sthpw/task['code','%s'].process)" % prntCode)
        cLogin = self.ser.eval('$LOGIN')
        pStype = self.ser.eval("@GET(sthpw/task['code','%s'].search_type)" % prntCode)
        cMsg = cTask['supervisor_comment']
        pSCode = self.ser.eval("@GET(sthpw/task['code','%s'].parent.code)" % prntCode)

        nData = {'note': cMsg, 'search_type': pStype, 'search_code': pSCode, 'process': cTaskProcs, 'login': cLogin,
                 'context': cTaskProcs}
        self.ser.insert('sthpw/note', data=nData)

        # ------------------------------- Take Increments ------------------------------


        cTk = self.ser.eval("@GET(sthpw/task['code','%s'].i_count)" % cCode)[0]

        nTkVal = int(cTk) + 1

        nTkTx = "I-Take{:02d}".format(nTkVal)

        self.ser.update(search_key=prntTask, data={'status': "Revise", 'take': nTkTx})
        self.ser.update(search_key=prntTask, data={'i_count': nTkVal})

    def clientApp(self):

        # --------------------------------

        ser = TacticServerStub()
        sKey = input.get("search_key")
        cCode = sKey.split("=")[-1]
        prntTask = ser.eval("@GET(sthpw/task['code','%s'].parent.org_task)" % cCode)
        # cTask=ser.eval("@SOBJECT(sthpw/task['code','%s'])"%cCode)[0]

        # ------------------------------- Approve Take Increments ------------------------------

        ser.update(search_key=prntTask, data={'status': "Approved"})

    def clientRject(self):

        pass

    def addReviewTask(self, inSKey=""):

        proj = self.ser.eval("$PROJECT")
        art = self.ser.eval("$LOGIN")
        sKey = input.get("search_key")
        cCode = sKey.split("=")[-1]
        cTaskDict = self.ser.eval("@SOBJECT(sthpw/task['code','%s'])" % cCode)[0]

        prc = cTaskDict['process']
        tak = cTaskDict['take']
        iCnt = cTaskDict['i_count']
        eCnt = cTaskDict['e_count']
        cSuper = cTaskDict['supervisor']
        prntName = self.ser.eval("@GET(sthpw/task['code','%s'].parent.name)" % cCode)[0]
        ep = self.ser.eval("@GET(sthpw/task['code','%s'].parent.%s/episode.name)" % (cCode, proj))[0]

        cName = "review of %s" % prntName
        desc = "created for %s's %s process" % (prntName, prc)
        res = self.ser.insert('%s/review_shot' % proj,
                              data={"name": cName, "description": desc, "take": tak, "org_task": sKey, 'episode': ep,
                                    'artist': art})
        resT = self.ser.create_task(search_key=res['__search_key__'], process="review", description=desc,
                                    assigned=cSuper)
        self.ser.update(search_key=resT['__search_key__'],
                        data={'status': 'Assignment', 'take': tak, 'i_count': iCnt, 'e_count': eCnt, 'epsiode': ep,
                              'task_process': prc})

    def addAssociateProductivity(self):

        pass

    def addPanel_asset(self, inSKey=""):

        proj = self.ser.eval("$PROJECT")
        inSK = inSKey
        cCode = inSK.split("=")[-1]
        cSObj = self.ser.eval("@SOBJECT($PROJECT/asset['code','%s'])" % cCode)[0]

        res_panel = self.ser.insert('%s/panel_asset' % proj,
                                    data={'name': cSObj['name'], 'episode_code': cSObj['episode_code']})
        exp = "@UPDATE(@SOBJECT($PROJECT/asset['code','%s']),'panel_asset_code','%s')" % (cCode, res_panel['code'])
        self.ser.eval(exp)

    def addPanel_shot(self, inSKey=""):

        proj = self.ser.eval("$PROJECT")

        inSK = inSKey
        cCode = inSK.split("=")[-1]
        cSObj = self.ser.eval("@SOBJECT($PROJECT/shot['code','%s'])" % cCode)[0]

        res_panel = self.ser.insert('%s/panel_shot' % proj,
                                    data={'name': cSObj['name'], 'sequence_code': cSObj['sequence_code']})
        exp = "@UPDATE(@SOBJECT($PROJECT/shot['code','%s']),'panel_shot_code','%s')" % (cCode, res_panel['code'])

        self.ser.eval(exp)

    def moveFeedBack(self):

        pass

    def spliShot_shot(self):

        '''

        ------------------------it is in WIP---------------------

        '''

        depots = {"DEPOT00002": "layout", "DEPOT00003": "anim", "DEPOT00004": "fx", "DEPOT00005": "lit",
                  "DEPOT00006": "ren", "DEPOT00007": "comp", "DEPOT00008": "edit"}

        cSkey = input.get("search_key")
        cCode = self.ser.split_search_key(search_key=cSkey)[-1]

        sTyp = "sthpw/task"

        shtStype = "demo_run_01/shot"

        subStype = "demo_run_01/sub_shot"

        inProc = self.ser.eval("@GET(sthpw/task['code','%s'].parent.depot_code)" % (cCode))[0]

        mShot = self.ser.eval("@GET(sthpw/task['code','%s'].parent.parent.code)" % (cCode))

        mTask = self.ser.eval(
            "@GET(%s['code','%s'].%s['process','%s'].code)" % (shtStype, mShot[0], sTyp, depots[inProc]))

        allInSubShots = self.ser.eval(
            "@GET(sthpw/task['code','%s'].parent.parent.%s['depot_code','%s'].code)" % (cCode, subStype, inProc))

        c = 0
        for i in allInSubShots:
            cStat = self.ser.eval("@GET(%s['code','%s'].%s.status)" % (subStype, i, sTyp))[0]
            if str(cStat) == "Complete":
                c += 1

        self.ser.start()

        sKey = self.ser.build_search_key("sthpw/task", code=mTask[0])

        if c == len(allInSubShots):
            self.ser.update(search_key=sKey, data={'status': "Complete"})
        else:
            self.ser.update(search_key=sKey, data={'status': "In Progress"})

        self.ser.finish()

    def splitAsset_asset(self):

        pass

    def addAdonAsset(self):

        pass

    def makeTodayLoginLog(self, day='$TODAY'):

        ts = []
        for i in self.ser.eval("@SOBJECT(sthpw/ticket['timestamp','>',$TODAY]['login',$LOGIN])"):
            ts.append(i.get('timestamp'))

        ts.sort()
        import datetime
        t1 = ts[0]
        t2 = ts[-1]
        datetimeFormat = '%Y-%m-%d %H:%M:%S.%f'
        difTime = datetime.datetime.strptime(t1, datetimeFormat) - datetime.datetime.strptime(t2, datetimeFormat)
        diffSec = abs(difTime.total_seconds())
        duration = datetime.timedelta(seconds=diffSec)
        cDate = datetime.datetime.now().date()
        mDt = datetime.datetime(2016, 01, 01) + duration
        cLogin = self.ser.eval('$LOGIN')
        self.chkSObjExistCreate(cStype='sthpw/login_log', cCol='login', cCode=cLogin, secCol='date', secVal=cDate,
                                inData={'login': cLogin, 'date': cDate.strftime("%Y-%m-%d"),
                                        'duration': mDt.strftime('%H:%M:%S')}, printOut=False, create=True, update=True)

    def addToBenchGrp(self, bGrp="", inUser='', inProj='', allProjects=False):

        if not allProjects:

            tCount = self.ser.eval(
                "@COUNT(sthpw/task['assigned','%s']['project_code','%s']['status','not in','Approved|I_App'])" % (
                inUser, inProj))

        else:

            tCount = self.ser.eval("@COUNT(sthpw/task['assigned','%s']['status','not in','Approved|I_App'])" % inUser)

        if not tCount:

            self.addToGroup(group=bGrp, user=inUser, project=inProj, remove=False)
        else:

            self.addToGroup(group=bGrp, user=inUser, project=inProj, remove=True)

    def updateBench(self, bnchGrp='bench', prj='dqe_theme_test_01', skipUsers=['gateway_gate'], globalProjects=False):

        for i in self.ser.eval('@SOBJECT(sthpw/login)'):

            if i['login'] not in skipUsers:
                self.addToBenchGrp(bGrp=bnchGrp, inUser=i['login'], inProj=prj, allProjects=globalProjects)

    def makeStatusReport(self, cEp='204', cStype='asset', skipProcess=['render_chk', 'edit']):
        self.ser.start()

        for i in self.ser.query(search_type='%s/%s' % (self.proj, cStype))[0:1]:

            for j in self.ser.get_pipeline_processes(search_key=i.get('__search_key__')):

                if j not in skipProcess:

                    pTypeDict = {'fur': 'asset', 'facial': 'asset', 'rigging': 'asset', 'texturing': 'asset',
                                 'asset_fx': 'asset', 'matte_painting': 'asset', 'master_lighting': 'asset',
                                 'modeling': 'asset', 'asset_comp': 'asset', 'layout': 'prod', 'blocking': 'prod',
                                 'secondary': 'prod', 'lip_sync': 'prod', 'fx': 'post', 'lighting': 'post',
                                 'render': 'post', 'comp': 'post', 'cloth_sim': 'post', 'hair_sim': 'post',
                                 'cloth_sim': 'post', 'fur_sim': 'post'}

                    expDict = {"process": j, 'episode': cEp, "pType": pTypeDict[j]}
                    actStatuses = {'YTS': 'YTS', 'WIP': "WIP", 'APP': 'Approved', 'HOLD': 'Hold', 'RETAKE': "Retake",
                                   'ISSUES': 'Issues'}
                    for s in ['YTS', 'WIP', 'APP', 'HOLD', 'RETAKE', 'ISSUES']:
                        expDict[s] = "@COUNT(sthpw/task['process','%s']['episode','%s']['status','%s'])" % (
                        j, cEp, actStatuses[s])
                        expDict[
                            s + '_%'] = "(@COUNT(sthpw/task['process','%s']['episode','%s']['status','%s'])*100.0)/(@COUNT(sthpw/task['process','%s']['episode','%s'])*1.0)" % (
                        j, cEp, actStatuses[s], j, cEp)
                    print expDict

                    self.chkSObjExistCreate(cStype='super4/status_report', cCol='process', cCode=j, secCol='episode',
                                            secVal=cEp, inData=expDict, printOut=True, create=True, update=False,
                                            delete=False)

        self.ser.finish()

    def getDQE_AssociateID(self, inDict={}, inKey='login'):

        if str(inDict[inKey]).startswith('P') or str(inDict[inKey]).startswith('p'):

            fName = int(inDict[inKey][1:])
            fName = "P%s" % fName
        else:
            fName = int(inDict['login'])
        return fName

    def makeTodayLoginLogGlobal(self, day='$TODAY'):

        for i in self.ser.query('sthpw/login'):

            ts = []
            for i in self.ser.eval("@SOBJECT(sthpw/ticket['timestamp','>',$TODAY]['login','%s'])" % i['login']):
                ts.append(i.get('timestamp'))

            if len(ts):
                ts.sort()
                import datetime
                t1 = ts[0]
                t2 = ts[-1]
                datetimeFormat = '%Y-%m-%d %H:%M:%S.%f'
                difTime = datetime.datetime.strptime(t1, datetimeFormat) - datetime.datetime.strptime(t2,
                                                                                                      datetimeFormat)
                diffSec = abs(difTime.total_seconds())
                duration = datetime.timedelta(seconds=diffSec)
                cDate = datetime.datetime.now().date()
                mDt = datetime.datetime(2016, 01, 01) + duration
                cLogin = i['login']

                print cLogin, duration
            self.chkSObjExistCreate(cStype='sthpw/login_log', cCol='login', cCode=cLogin, secCol='date', secVal=cDate,
                                    inData={'login': cLogin, 'date': cDate.strftime("%Y-%m-%d"),
                                            'duration': mDt.strftime('%H:%M:%S')}, printOut=False, create=True,
                                    update=True)

    def clear_tickets(self, user=""):

        for i in self.ser.eval("@SOBJECT(sthpw/ticket['login','%s'])" % user):
            self.ser.delete_sobject(search_key=i['__search_key__'], include_dependencies=False)

    def makeDayDuration(self):

        try:
            pyLgn = int(self.ser.eval('$LOGIN'))
        except:
            pyLgn = self.ser.eval('$LOGIN').split('.')[0]

            cDate = str(datetime.datetime.now()).split(' ')[0]
            coTime = int(time.time())
            loTs = str(datetime.datetime.now()).split('.')[0]

            pyLoginLog = self.ser.eval("@SOBJECT(sthpw/login_log['date','%s']['login','%s'])" % (cDate, pyLgn))
        if len(pyLoginLog):
            pyDifTime = abs(int(pyLoginLog[0]['start_time']) - coTime)
            tDur = time.strftime("%H:%M:%S", time.gmtime(pyDifTime))
            self.ser.update(search_key=pyLoginLog[0]['__search_key__'],
                            data={'signout_time': loTs, 'end_time': coTime, 'duration': tDur})

    def makeProjectAttndance(self):

        cTime = str(time.time()).split('.')[0]
        cDate = str(datetime.datetime.now()).split(' ')[0]
        proj = self.ser.eval('$PROJECT');

        try:
            lgn = int(self.ser.eval('$LOGIN'))
        except:
            lgn = self.ser.eval('$LOGIN').split('.')[0]

            expRes = self.ser.eval(
                "@COUNT(sthpw/dqe_dlf_project_pulse['date','%s']['login','%s']['project','%s'])" % (cDate, lgn, proj))

            if (expRes < 1):
                self.ser.insert(search_type='sthpw/dqe_dlf_project_pulse',
                                data={'project': proj, 'login': lgn, 'date': cDate})

            expRes = self.ser.eval("@COUNT(sthpw/login_log['date','%s']['login','%s'])" % (cDate, lgn));

            if (expRes < 1):
                self.ser.insert(search_type='sthpw/login_log', data={'login': lgn, 'start_time': cTime, 'date': cDate})

    def correspondingTaskUpades(self, pro='', epNum='', sTyp='shot', srcCol='', destCol='', srcPrc='', destPrc=''):

        shotDict = {}

        for i in a.ser.eval("@SOBJECT(sthpw/task['process','%s']['episode','%s'])" % (srcPrc, epNum)):
            shotDict[i['search_code']] = i[srcCol]

        for i in shotDict.keys():
            a.ser.eval(
                "@UPDATE(@SOBJECT(super4/%s['code','%s'].sthpw/task['process','%s']['episode','%s']),'%s','%s')" % (
                sTyp, i, destPrc, epNum, destCol, shotDict[i]))

    def makeProcessReport(self):

        tabl = "<html>"

        tabl += """

        <style>
        table {
            font-family: arial, sans-serif;
            border-collapse: collapse;
            width: 60%;
        }

        .td, th {
            border: 1px solid #000000;
            text-align: left;
            padding: 8px;
        }

        .tit {
            border: 1px solid #dddddd;
            text-align: center;
            font-weight:bold;
            padding: 10px;
            background-color: #66aaff;
            color:#fff;


        }

        tr:nth-child(even) {
            background-color: #dddddd;

        }

        .incomingCls {
            background-color: #aaaaff;
            border: 1px solid #dddddd;
            text-align: center;
            font-weight:bold;
            padding: 10px;
        }

        .dateRangeCls {
            background-color: #66ff66;
            border: 1px solid #dddddd;
            text-align: center;
            font-weight:bold;
            padding: 10px;
        }

        .pendingCls {
            background-color: #ff6666;
            border: 1px solid #dddddd;
            text-align: center;
            font-weight:bold;
            padding: 10px;
        }

        .ripCls {
            background-color: #ccffcc;
            border: 1px solid #dddddd;
            text-align: center;
            font-weight:bold;
            padding: 10px;
        }

        .y2lCls {
            background-color: #ff3333;
            border: 1px solid #dddddd;
            text-align: center;
            font-weight:bold;
            padding: 10px;
        }

        .filters

        {
            width:85%;
            height:60px;
            background-color: #ddddff;
            float:left;

        }

        .filtersTitles
        {
            float:left;
            margin:10px;
            hegiht:30px;
            padding:5px;
            border-radius:5px;
        }

        .btn_rep_gt,.projectFilter
        {
            float:left;
            margin:10px;
            hegiht:30px;
            padding:5px;
            border-radius:5px;
            width:200px;
        }

        </style>
        """

        cProject = 'super4'

        tabl += '<div class="filters">'
        tabl += '<p class="filtersTitles">Project:</p>'
        tabl += '<select class="projectFilter" select="super4">'
        allProjects = a.ser.eval('@GET(sthpw/project.code)')

        for k in ['admin', 'no_project', 'sthpw', 'dqe_dlf']:
            allProjects.remove(k)

        allProjects.append("All Projects")

        for i in allProjects:

            if i == cProject:

                tabl += '<option value="{0}" selected>{0}</option>'.format(i)
            else:

                tabl += '<option value="{0}">{0}</option>'.format(i)

        tabl += "</select>"
        tabl += '<p class="filtersTitles">Period:</p>'
        tabl += '<input class="btn_rep_gt" type="date" width="150" id="sDate_gt" onChange="priodChange()" />'
        tabl += '<input class="btn_rep_gt" type="date" width="150" id="eDate_gt" onChange="priodChange()"/>'

        tabl += '<input class="btn_rep_gt" type="button" value="Show" width="150" id="show_btn" />'
        tabl += "</div>"
        tabl += "<table>\n"

        eps = []

        for e in range(200, 253):

            epCout = a.ser.eval(
                "@COUNT(sthpw/task['process','render']['episode','{0}']['status','not in','YTS'])".format(e))
            if epCout:
                eps.append(e)

        rrcols = ['Project', 'Episode', 'Sec_in', 'Total_in', 'Fresh_in', '3DC_in', 'BG_in', 'CHAR_in',
                  'Total_sec_today', 'Fresh_sec_today', '3DC_sec_today', 'Total_today', 'Fresh_today', '3DC_today',
                  "BG_today", "CHAR_today", 'Total_sec_pen', 'Fresh_pen', '3DC_pen', 'BG_pen', 'CHAR_pen', 'Total_rip',
                  'Fresh_rip', '3DC_rip', 'Total_y2l', 'Fresh_y2l', '3DC_y2l']

        nonAnch = ['Project', 'Episode', 'Sec_in']

        for t in range(2):

            tabl += "\t<tr>\n"

            if t == 1:

                for j in range(len(rrcols)):

                    if j > 1 and j < 8:

                        tabBG = "incomingCls"
                    elif j > 7 and j < 16:
                        tabBG = "dateRangeCls"
                    elif j > 15 and j < 21:

                        tabBG = "pendingCls"
                    elif j > 20 and j < 24:

                        tabBG = "ripCls"
                    elif j > 23:

                        tabBG = "y2lCls"
                    else:

                        tabBG = "tit"

                    tabl += '\t\t<td class="{2}" id="{0}">{1}</td>\n'.format(rrcols[j], rrcols[j].split("_")[0], tabBG)

            elif t == 0:

                for j in range(len(rrcols)):

                    if j == 0 and j < 3:

                        spanCnt = 2
                        if j == 0:
                            tabl += '\t\t<td class="{1}" colspan="{0}"></td>\n'.format(spanCnt, "tit")


                    elif j > 2 and j < 8:

                        spanCnt = 6

                        if j == 3:
                            tabl += '\t\t<td class="{1}" colspan="{0}">Incoming</td>\n'.format(spanCnt, "tit")


                    elif j > 7 and j < 16:
                        spanCnt = 8

                        if j == 8:
                            tabl += '\t\t<td class="{1}" id="periodTitle" colspan="{0}">Between selected {2} to {3}</td>\n'.format(
                                spanCnt, "tit", '20-09-2016', '24-09-2016')


                    elif j > 15 and j < 21:

                        spanCnt = 5

                        if j == 16:
                            tabl += '\t\t<td class="{1}" colspan="{0}">Pending</td>\n'.format(spanCnt, "tit")



                    elif j > 20 and j < 24:

                        spanCnt = 3

                        if j == 21:
                            tabl += '\t\t<td class="{1}" colspan="{0}">Render in Progress</td>\n'.format(spanCnt, "tit")


                    elif j > 23:

                        spanCnt = 3

                        if j == 24:
                            tabl += '\t\t<td class="{1}" colspan="{0}">Yet to Launch</td>\n'.format(spanCnt, "tit")

            tabl += "</tr>"

        for i in range(len(eps)):

            rrcolsData = []

            rrcolsData.append(cProject)
            rrcolsData.append(eps[i])

            # ----------------------------Incomming----------------------------

            rrcolsData.append(40.5)
            rrcolsData.append(10)
            rrcolsData.append(7)
            rrcolsData.append(3)
            rrcolsData.append(0)
            rrcolsData.append(10)

            # ----------------------------------- Completed-------------------------

            rrcolsData.append(500)
            rrcolsData.append(120)
            rrcolsData.append(380)
            rrcolsData.append(45)
            rrcolsData.append(15)
            rrcolsData.append(30)
            rrcolsData.append(0)
            rrcolsData.append(45)

            # -------------------------Pending--------------------------

            rrcolsData.append(1200)
            rrcolsData.append(400)
            rrcolsData.append(800)
            rrcolsData.append(0)
            rrcolsData.append(1200)

            # --------------------------------RIP-----------------------

            rrcolsData.append(400)
            rrcolsData.append(150)
            rrcolsData.append(250)

            # ----------------------------------YTL---------------------
            rrcolsData.append(800)
            rrcolsData.append(600)
            rrcolsData.append(200)

            tabl += "\t<tr>\n"
            for j in range(len(rrcols)):

                if j > 1:

                    dataCls = "dataCls"
                else:

                    dataCls = "tit"

                if rrcols[j].find('sec') != -1 or rrcols[j] in nonAnch:

                    cellData = rrcolsData[j]

                else:

                    cellData = '<a href="" onClick="myAlert({1});">{0}</a>'.format(rrcolsData[j], rrcolsData[1])

                tabl += '\t\t<td class="{2}" id="{0}">{1}</td>\n'.format(rrcols[j], cellData, dataCls)

            tabl += "</tr>"

        tabl += "</table>"

        tabl += """
        <script>

        function myAlert(inEp)
        {

        sDate=document.getElementById("sDate_gt").value;
            alert(inEp);
        }

        function priodChange()
        {

            var sDate=document.getElementById("sDate_gt").value;
            var eDate=document.getElementById("eDate_gt").value;
            sDate=document.getElementById("periodTitle").innerHTML="Between selected "+sDate+" to "+eDate;

        }

        </script>
        """

        tabl += "</html>"

        with open('C:/Users/user/Desktop/tsetTable/table.html', 'w') as f:

            f.write(tabl)


'''---------------------------------------------------------super 212---------------------------------------------------------------'''

a = GatewayMaster(xlspath="C:/Users/user/Desktop/s4_202_docs/HRU_221_TBL_RICKY_RICTUS _20151214_VDEF_DQ.xls")

'''
for i in a.getDataFromExcelRemap(startRow=7, endRow=213,getSel=0, rawCols=[ 'Shot', 'frames' , 'time_in_day', 'environment', 'sequence', 'COMMENTS'], shtName='221_TBL', remap=[]):

    print (i)

a.makeShotsExcel(cEp='221', SheetName='221_TBL', iStartRow=7, iEndRow=213, iRawCols=[ 'Shot', 'frames' , 'time_in_day', 'environment', 'sequence', 'COMMENTS'], iRemap=[ 'name', 'frame', 'time_in_day', 'environment', 'sequence_code', 'description'])
'''
cEp = '221'

for i in a.ser.eval("@SOBJECT(super4/shot['ep_num','221'])")[0:]:

    res = a.ser.add_initial_tasks(search_key=i['__search_key__'], pipeline_code='super4/shot',
                                  processes=['secondary', 'lighting', 'comp', 'render', 'render_chk'],
                                  skip_duplicate=True)

    for p in ['secondary', 'lighting', 'comp', 'render', 'render_chk']:
        ct = a.ser.eval("@SOBJECT(sthpw/task['search_code','{0}']['process','{1}'])".format(i['code'], p))[0]
        a.ser.update(search_key=ct['__search_key__'],
                     data={'episode': cEp, 'i_count': 1, 'e_count': 0, 'take': 'INT-Take01'})

for i in a.ser.eval("@SOBJECT(super4/shot['ep_num','212'])")[0:]:

    res = a.ser.add_initial_tasks(search_key=i['__search_key__'], pipeline_code='super4/shot',
                                  processes=['secondary', 'lighting', 'comp', 'render', 'render_chk'],
                                  skip_duplicate=True)

    for p in ['secondary', 'lighting', 'comp', 'render', 'render_chk']:
        ct = a.ser.eval("@SOBJECT(sthpw/task['search_code','{0}']['process','{1}'])".format(i['code'], p))[0]
        a.ser.update(search_key=ct['__search_key__'],
                     data={'episode': cEp, 'i_count': 1, 'e_count': 0, 'take': 'INT-Take01'})

'''
    for ct in res:

        a.ser.update(search_key=ct['__search_key__'],data={'episode':cEp,'i_count':1,'e_count':0,'take':'INT-Take01'})
'''

