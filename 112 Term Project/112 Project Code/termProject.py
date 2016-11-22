from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from panda3d.core import CollisionTraverser, CollisionNode
from panda3d.core import CollisionHandlerQueue, CollisionRay
from panda3d.core import Filename, AmbientLight, DirectionalLight
from panda3d.core import PandaNode, NodePath, Camera, TextNode
from panda3d.core import CollideMask
from direct.gui.OnscreenText import OnscreenText
from direct.actor.Actor import Actor
import random
import sys
import os
import math


class App(ShowBase):
    
    
    def __init__(self):
        ShowBase.__init__(self)
            
        self.actorBullet = 0
        
        self.keyMap = {"cam-up": False, "cam-down": False, "cam-left":False, "cam-right": False, "up":False, "down":False, "left": False, "right":False, "shoot": False}
        
        #load environment model
        self.environ = loader.loadModel("models/world")
        self.environ.reparentTo(render)
        
        #load actor
        actorStartPos = self.environ.find("**/start_point").getPos()
        self.actor = Actor("models/ralph",{"run": "models/ralph-run", "walk":"models/ralph-walk"})
        self.actor.reparentTo(render)
        self.actor.setScale(.2)
        self.actor.setPos(actorStartPos+(0,0,0))
        
        #load bullets
        for bullets in range(self.actorBullet):
            print("making bullet")
            bullet = loader.loadModel("models/smiley")
            bullet.reparentTo(render)
            bullet.setPos(self.actor.getPos())

        
        #load floater which is the point of focus for the camera
        self.floater = NodePath(PandaNode("floater"))
        self.floater.reparentTo(self.actor)
        self.floater.setZ(2.0)
        
        
        self.disableMouse()
        # base.useDrive()
        self.camera.setPos(self.actor.getX(), 
                        self.actor.getY()+10,
                            2.0)
        self.camera.lookAt(self.floater)
                            
        #event handlers
        self.accept("arrow_up", self.setKey, ["cam-up",True])
        self.accept("arrow_up-up", self.setKey, ["cam-up", False])
        self.accept("arrow_down", self.setKey, ["cam-down",True])
        self.accept("arrow_down-up", self.setKey, ["cam-down", False])
        self.accept("arrow_left", self.setKey, ["cam-left",True])
        self.accept("arrow_left-up", self.setKey, ["cam-left", False])
        self.accept("arrow_right", self.setKey, ["cam-right",True])
        self.accept("arrow_right-up", self.setKey, ["cam-right", False])
        self.accept("w", self.setKey, ["up", True])
        self.accept("w-up", self.setKey, ["up", False])
        self.accept("a", self.setKey, ["left", True])
        self.accept("a-up", self.setKey, ["left", False])
        self.accept("s", self.setKey, ["down", True])
        self.accept("s-up", self.setKey, ["down", False])
        self.accept("d", self.setKey, ["right", True])
        self.accept("d-up", self.setKey, ["right", False])
        self.accept("space", self.setKey, ["shoot", True])
        self.accept("space-up", self.setKey, ["shoot", False])
                        
        taskMgr.add(self.moveCamera, "moveCamera")
        
        self.isMoving = False
        
        #create collision traverser which handles all the collision stuff
        self.Traverser = CollisionTraverser()
        
        #create solid
        self.actorGroundRay = CollisionRay()
        #set origin and direction of the collision ray
        self.actorGroundRay.setOrigin(0, 0, 9)
        self.actorGroundRay.setDirection(0, 0, -1)
        #create the collision node
        self.actorGroundCol = CollisionNode('ralphRay')
        #attach solid to node
        self.actorGroundCol.addSolid(self.actorGroundRay)
        #attach node to actor. Create the node path
        self.actorGroundColNp = self.actor.attachNewNode(self.actorGroundCol)
        #create queue
        self.actorGroundHandler = CollisionHandlerQueue()
        #add nodepath and queue to traverser
        self.Traverser.addCollider(self.actorGroundColNp, self.actorGroundHandler)
        
        
        
        
        #show collision node 
        # self.actorGroundColNp.show()
        
 
 
   
    def setKey(self, key, val):
        print(key, val)
        self.keyMap[key]=val
        
    def moveCamera(self, task):
        dt = globalClock.getDt()
        
        startPos = self.actor.getPos()
        
        #camera control
        if self.keyMap["cam-up"]:
            self.camera.setZ(self.camera, 20*dt)
        if self.keyMap["cam-down"]:
            self.camera.setZ(self.camera, -20*dt)
        if self.keyMap["cam-left"]:
            self.camera.setH(self.camera.getH()+20*dt)
        if self.keyMap["cam-right"]:
            self.camera.setH(self.camera.getH()-20*dt)
            
       
        print(self.camera.getH())
            
        #character control    
        if self.keyMap["up"]:
            self.actor.setY(self.actor,-20*dt)
        if self.keyMap["down"]:
            self.actor.setY(self.actor, +20*dt)
        if self.keyMap["left"]:
            self.actor.setH(self.actor.getH()+300*dt)
        if self.keyMap["right"]:
            self.actor.setH(self.actor.getH()-300*dt)
        if self.keyMap["shoot"]:
            self.actorBullet +=1
            
            
        #make the animation of ralph running
        if self.keyMap["up"] or self.keyMap["down"] or self.keyMap["right"]:
            if self.isMoving == False:
                self.actor.loop("run")
                self.isMoving = True
        else:
            if self.isMoving:
                self.actor.stop()
                self.actor.pose("walk", 5)
                self.isMoving = False
                
                
        #control the camera so that it is always a distance away from ralph
        camvec = self.actor.getPos() - self.camera.getPos()
        camvec.setZ(0)
        camdist = camvec.length()
        camvec.normalize()
        if camdist > 10.0:
            self.camera.setPos(self.camera.getPos() + camvec * (camdist - 10))
            camdist = 10.0
        if camdist < 5.0:
            self.camera.setPos(self.camera.getPos() - camvec * (5 - camdist))
            camdist = 5.0
            
        self.Traverser.traverse(render)
        actorEntries = list(self.actorGroundHandler.getEntries())
        actorEntries.sort(key=lambda x: x.getSurfacePoint(render).getZ())
        
        if len(actorEntries)>0 and actorEntries[0].getIntoNode().getName() == "terrain":
            self.actor.setZ(actorEntries[0].getSurfacePoint(render).getZ())
        else:
            self.actor.setPos(startPos)
        

        self.camera.lookAt(self.floater)
        
        return task.cont



demo = App()
demo.run()

