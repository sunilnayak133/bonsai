#Bonsai for Maya
#Author - Sunil Nayak
#Version 3.0

import maya.cmds as cmds
import PySide2.QtCore as qc
import PySide2.QtGui as qg
import PySide2.QtWidgets as qw
import functools 
import math
import random

def selFlat():
	return cmds.ls(sl=1, flatten = True)

#class to set up the UI to rename the object when finalized
class Renamer(qw.QDialog):
	numFinalized=1
	
	def __init__(self, parentWidget):
		#init the main dialog
		qw.QDialog.__init__(self)

		self.parentWidget = parentWidget
		#set window title
		self.setWindowTitle('Bonsai for Maya - Name The Tree')
		self.setFixedWidth(400)

		self.setLayout(qw.QVBoxLayout())

		self.namePrompt = qw.QLabel('Name the tree')

		self.namefield = qw.QLineEdit()
		self.namefield.setText('Tree'+str(Renamer.numFinalized))
		self.namefield.textChanged.connect(self.CheckValidName)		

		self.btnname = qw.QPushButton('Finalize Name')
		self.btnname.clicked.connect(self.RenameIt)

		self.helpText = qw.QLabel('An object with this name already exists')

		self.helpText2 = qw.QLabel('Name Cannot Be Empty')

		self.layout().addWidget(self.namePrompt)
		self.layout().addWidget(self.namefield)

		self.CheckValidName()

	#to check if the name is valid
	def CheckValidName(self):
		sl = cmds.ls(self.namefield.text())
		if(self.namefield.text()==''):
			self.namefield.setStyleSheet("background-color: red")
			self.btnname.setParent(None)
			self.helpText.setParent(None)
			self.layout().addWidget(self.helpText2)
		else:
			if(len(sl)!=0):
				self.namefield.setStyleSheet("background-color: red")
				self.btnname.setParent(None)
				self.helpText.setParent(None)
				self.layout().addWidget(self.helpText)
			else:
				self.namefield.setStyleSheet("background-color: green")
				self.btnname.setParent(None)
				self.helpText.setParent(None)
				self.helpText2.setParent(None)
				self.layout().addWidget(self.btnname)
	#to actually rename it
	def RenameIt(self):
		cmds.rename('treeObject', self.namefield.text())
		self.parentWidget.close()
		self.close()



def ShowRenamer():
	namer = Renamer()
	namer.show()

#class that does the tree generation 
class BonsaiUI(qw.QDialog):
	#set up UI, hook up sliders and connections
	def __init__(self):
		#init the main dialog
		qw.QDialog.__init__(self)
		#set window title
		self.setWindowTitle('Bonsai for Maya')
		self.setFixedWidth(400)

		self.tabs = qw.QTabWidget()
		self.tab1 = qw.QDialog()
		self.tab2 = qw.QDialog()
		self.tabs.setFixedWidth(375)

		self.tabs.addTab(self.tab1,"Trunk")
		self.tabs.addTab(self.tab2,"Branches")

		self.minBL = 1
		self.maxBL = 20
		self.bend = ["",""]
		self.flare = ["",""]
		self.trunk = ["",""]
		self.branches = ""
		self.branchBendHandles = []
		self.midbend = ["",""]

		#init sliders,
		#connect to slideApply functions to make dynamic editing possible		
		#height slider
		self.ht = qw.QSlider(qc.Qt.Horizontal)
		self.ht.setMinimum(1)
		self.ht.setMaximum(30)
		self.ht.valueChanged.connect(self.slideApply)
		self.ht.setValue(20)        

		#curvature
		self.cu = qw.QSlider(qc.Qt.Horizontal)
		self.cu.setMinimum(-50)
		self.cu.setMaximum(50)
		self.cu.valueChanged.connect(self.curveSlideApply)
		self.cu.setValue(0)

		#midCurvature
		self.mc = qw.QSlider(qc.Qt.Horizontal)
		self.mc.setMinimum(-50)
		self.mc.setMaximum(50)
		self.mc.valueChanged.connect(self.curveSlideApply)
		self.mc.setValue(0)

		#bottom radius - divide by 10
		self.br = qw.QSlider(qc.Qt.Horizontal)
		self.br.setMinimum(1)
		self.br.setMaximum(10)
		self.br.valueChanged.connect(self.slideApply)
		self.br.setValue(10)

		#top radius - divide by 10
		self.tr = qw.QSlider(qc.Qt.Horizontal)
		self.tr.setMinimum(1)
		self.tr.setMaximum(10)
		self.tr.valueChanged.connect(self.slideApply)
		self.tr.setValue(1)

		#branch level
		self.bl = qw.QSlider(qc.Qt.Horizontal)
		self.bl.setMinimum(self.minBL)
		self.bl.setMaximum(self.maxBL)
		self.bl.valueChanged.connect(self.slideApply)
		self.bl.setValue(self.maxBL)

		#branch curvature
		self.bc = qw.QSlider(qc.Qt.Horizontal)
		self.bc.setMinimum(0)
		self.bc.setMaximum(100)
		self.bc.valueChanged.connect(self.slideApply)
		self.bc.setValue(40)

		#number of branches
		self.nb = qw.QSlider(qc.Qt.Horizontal)
		self.nb.setMinimum(0)
		self.nb.setMaximum(12)
		self.nb.valueChanged.connect(self.slideApply)
		self.nb.setValue(5)

		#length of branches
		self.lb = qw.QSlider(qc.Qt.Horizontal)
		self.lb.setMinimum(3)
		self.lb.setMaximum(12)
		self.lb.valueChanged.connect(self.slideApply)
		self.lb.setValue(5)

		#leaf pair count
		self.lp = qw.QSlider(qc.Qt.Horizontal)
		self.lp.setMinimum(10)
		self.lp.setMaximum(20)
		self.lp.valueChanged.connect(self.slideApply)
		self.lp.setValue(10)

		#apply button, link to apply function
		self.btnapp = qw.QPushButton('Apply')
		self.btnapp.clicked.connect(functools.partial(self.apply))

		self.btnfin = qw.QPushButton('Finalize')
		self.btnfin.clicked.connect(functools.partial(self.Finalize))
		self.btnfin.setStyleSheet("background-color: green")
		
		self.tab1.setLayout(qw.QFormLayout())
		self.tab2.setLayout(qw.QFormLayout())
		self.tab1.layout().addRow('Height:', self.ht)
		self.tab1.layout().addRow('Bottom Curvature:', self.cu)
		self.tab1.layout().addRow('Middle Curvature:', self.mc)
		self.tab1.layout().addRow('Bottom Radius:', self.br)
		self.tab1.layout().addRow('Top Radius:', self.tr)
		self.tab1.layout().addRow(' ',None)
		#self.layout().addRow(' ',None)
		#self.layout().addRow('Branch Information', None)
		#self.layout().addRow(' ',None)
		self.tab2.layout().addRow('Number of Branches:', self.nb)
		self.tab2.layout().addRow('Branch Level:', self.bl)
		self.tab2.layout().addRow('Branch Curvature:', self.bc)
		self.tab2.layout().addRow('Branch Length:', self.lb)
        #self.tab2.layout().addRow('Leaf Pair Count:', self.lp)
				
		self.setLayout(qw.QVBoxLayout())
		self.layout().addWidget(self.tabs)
		self.layout().addWidget(self.btnapp)
		self.layout().addWidget(self.btnfin)
	#the function that's called when any slider moves
	def slideApply(self):
		sl = cmds.ls('treeObject')
		if(len(sl)!=0):
			self.apply()
		else:
			return

	#the function that's called when the apply button is pressed
	def apply(self):
		sl = cmds.ls(['treeObject', 'Branches'])
		if(len(sl)!=0):
			cmds.delete(sl)

		h = self.ht.value()
		c = self.cu.value()
		br = float(self.br.value())/10.0
		tr = float(self.tr.value())/10.0
		bc = self.bc.value()
		nb = self.nb.value()
		lb = self.lb.value()
		mc = self.mc.value()
		lp = self.lp.value()
		self.blvl = self.bl.value()
		self.trunk = self.Apply(pHt = h, pCurv = c, pMidCurv = mc, pBr = br, pTr = tr, pLevel = self.blvl, pBrLen = lb, pNumBranches = nb, pBrCurv = bc, pLP = lp)
		#cmds.delete(trunk, ch=True)
		#cmds.rename(self.trunk, 'treeObject')
		self.trunk = 'treeObject'

	#the function that's called when the curvature slider is moved
	def curveSlideApply(self):
		sl = cmds.ls(self.bend[0])
		if(len(sl)==0):
			return
		else:
			cmds.setAttr(self.bend[0]+'.curvature', self.cu.value())	
		sl = cmds.ls(self.midbend[0])
		if(len(sl)==0):
			return
		else:
			cmds.setAttr(self.midbend[0]+'.curvature', self.mc.value())		

	#make the tree using a cylinder
	def makeTree(self, pHt=20,pSy = 20, pSz = 3, pR=1):
		trunk = cmds.polyCylinder(h = pHt, sy = pSy, sz = pSz, r = pR)
		cmds.xform(trunk, translation = [0,pHt/2,0], piv = [0,-pHt/2,0])
		return trunk

	#apply flare
	def applyFlare(self, pTrunk, pBr=1, pTr = 0.1):
		flare = cmds.nonLinear(pTrunk, typ = "flare")
		flvals = {"startFlareX" : pBr, "startFlareZ" : pBr, "endFlareX" : pTr, "endFlareZ" : pTr}
		for key in flvals:
			cmds.setAttr(flare[0]+"."+key, flvals[key])
		return flare


	#bend the tree using bend deformer
	def bendTrunk(self, pTrunk, pCurv):
		bend = cmds.nonLinear(pTrunk, typ = "bend", curvature = pCurv)		
		cmds.xform(bend[1], translation = [0,0,0])
		return bend

	#get the point in the middle of the trunk at a perticular level
	def trunkMiddle(self, pTrunk, pLevel, pSa = 20):
		sf = (pLevel + 1) * pSa
		ef = sf + pSa
		frange = str(sf) + ':' + str(ef)
		cmds.select(pTrunk + '.f[' + frange + ']',r = True)
		faces = selFlat()				
		p = cmds.xform(faces,q=True,bb=True, ws=True)
		p = [(p[0]+p[3])/2.0,(p[1]+p[4])/2.0,(p[2]+p[5])/2.0]
		return p

	#bend deformer for the middle of the trunk
	def midBendTrunk(self, pTrunk, pCurv, pSy, pSa):
		midbend = cmds.nonLinear(pTrunk, typ = "bend", curvature = pCurv)
		p = self.trunkMiddle(pTrunk,pSy/2, pSa)
		cmds.xform(midbend[1], translation = p)
		cmds.setAttr(midbend[0]+'.lowBound',0)
		return midbend

	#generate a pair of leaves
	def leafPair(self, pR = 0.5, pH = 3):
		l = cmds.polyCylinder(r=pR,h=pH,sy=10,n='leaf')
		cmds.xform(l,t = [0,float(pH)/2.0,0], piv=[0,float(-pH)/2.0,0])
		fl = cmds.nonLinear(l[0], typ = "flare")
		fld = {".startFlareX":0.5, ".endFlareX":0.1, ".startFlareZ":0.1, ".endFlareZ":0.1}
		for i in fld:
			cmds.setAttr(fl[0]+i, fld[i])
		cmds.delete(l[0],ch=True)
		cmds.xform(l[0],ro=[100,90,0])
		d = cmds.duplicate(l[0],n='leaf2')
		cmds.xform(d,ro=[180,0,180],r = True)
		l1 = cmds.polyUnite(l[0],d,n='leaves')
		cmds.delete(l1,ch=True)
		cmds.xform(l1[0],ro=[-90,0,0])
		return l1[0]


	#place one branch, make sure the branch (when spawned) is pointed "up" wrt the trunk
	#add bend deformer to it, then duplicate and rotate (both branch and deformer)
	#after this, add bend to the trunk
	def placeBranches(self, pTrunk, pLevel, pBranchHeight = 7, pBr = 0.1, pTr=0.05, pSa=20, pCurv = 40, pNumBranches = 5, pLP=10):
		#if branches exist already, delete them
		b = cmds.ls(self.branches)
		if(len(b)!=0):
			cmds.delete(self.branches)

		if(pNumBranches == 0):
			g = ''
			return g

		#find the position of the face to put the first branch at
		p = self.trunkMiddle(pTrunk, pLevel)

		count = 0
		branches = []
		bb = []

		#make the first branch
		bn = 'branch' + str(count)
		c = cmds.polyCylinder(r = pBr, h = pBranchHeight, sa = 20, sh = 20, n = bn)	
		cmds.xform(c, t = [0,pBranchHeight/2,0], piv = [0,-pBranchHeight/2,0])

		'''
		#make leaves
		leaves = []
		for i in range(1,pLP):
			lp = self.leafPair(pH=3.0/float(i))
			cmds.xform(lp, t=[0,i*pBranchHeight/pLP,0])
			cmds.rename(lp, 'lp'+str(i))
			lp = 'lp'+str(i)
			leaves.append(lp)		
		bn = cmds.polyUnite(bn,leaves, n='leaved'+bn)
		bn = bn[0]
		cmds.xform(bn, piv = [0,0,0])
		cmds.delete(bn,ch=True)
		'''

		branches.append(bn)
		count += 1
		cmds.xform(c,t=p, ws=True,relative=True)
		rp = cmds.xform(bn, q = True, rp = True, ws = True)
		thisbb = cmds.nonLinear(typ = "bend", curvature = pCurv)
		bb.append(thisbb)
		cmds.xform(thisbb[1], translation = rp, ws = True)
		self.setBendAttrs(thisbb[0])

		#delete history for first branch
		cmds.delete(bn, ch=True)

		#duplicate it
		if(pNumBranches>0):
			angBetweenBranches = 360/pNumBranches
		else:
			angBetweenBranches = 360
		for i in range(1,pNumBranches):
			newbn = 'branch' + str(count)
			branches.append(newbn)
			cmds.duplicate(bn, name = newbn)
			bn = newbn
			count += 1
			cmds.xform(newbn, ro=[0,angBetweenBranches,0], relative = True)		
		
		g = cmds.group(branches, n = 'Branches')
		return g
		#return 0

	def setBendAttrs(self, bend):		
		cmds.setAttr(bend+'.lowBound',0)
		cmds.setAttr(bend+'.highBound',10)

	#bending the branches - probably obsolete now
	def bendBranches(self, blist, pCurv=40):
		branchBendHandles = []
		for i in blist:
			rp = cmds.xform(i, q = True, rp = True, ws = True)
			cmds.select(i, r = True)
			#cmds.manipPivot(o=ro)
			bb = cmds.nonLinear(typ = "bend", curvature = pCurv)
			cmds.xform(bb[1], translation = rp, ws = True)
			#cmds.manipPivot(o=[0,0,0])
			branchBendHandles.append(bb[1])
		return branchBendHandles

	#Apply - to simplify the older apply function callback - uses the class attributes as parameters	
	def Apply(self, pHt=20, pSa = 20, pSy=20, pSz=3, pBr=1, pTr=0.1, pCurv=20, pMidCurv = -20, pLevel = 17, pBrLen = 3, pNumBranches = 5, pBrCurv = 40, pLP = 10):
		trunk = self.makeTree(pHt,pSy,pSz,max(pBr,pTr))
		self.flare = self.applyFlare(trunk[0],pBr,pTr)
		#the order below will have to be swapped
		self.branches = self.placeBranches(trunk[0], pLevel, pBranchHeight = pBrLen, pNumBranches = pNumBranches, pCurv = pBrCurv, pLP = pLP)
		trunk = trunk[0]
		if(self.branches!=''):
			trunk = cmds.polyUnite(trunk, self.branches, n = 'treeObject')[0]
		else:
			cmds.rename(trunk, 'treeObject')
			trunk = 'treeObject'
		cmds.delete(ch=True)
		self.bend = self.bendTrunk(trunk, pCurv)
		self.midbend = self.midBendTrunk(pTrunk = trunk, pCurv = pMidCurv, pSy = pSy, pSa = pSa)
		return trunk

	#finalize the mesh - and name it
	def Finalize(self):		
		if(self.trunk == 'treeObject'):
			cmds.delete(self.trunk,ch=True)			
			cmds.select(self.trunk)			
			namer = Renamer(self)
			namer.exec_()
			namer.show()			
		else:
			self.close()

	def pop(self):
		self.window = Pop()

#show the UI
t = BonsaiUI()
t.show()

