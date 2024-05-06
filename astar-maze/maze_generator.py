import random, datetime, csv, os
from tkinter import *
from enum import Enum
from collections import deque


class COLOR(Enum):
    dark=('gray11','white')
    light=('white','black')
    black=('black','dim gray')
    red=('red3','tomato')
    green=('green4','pale green')
    blue=('DeepSkyBlue4','DeepSkyBlue2')
    yellow=('yellow2','yellow2')


class Agent:
    def __init__(
            self,
            parentMaze,
            x=None,
            y=None,
            shape='square',
            goal=None,
            filled=False,
            footprints=False,
            color:COLOR=COLOR.blue
    ):
        self.parent_maze=parentMaze
        self.color=color

        if isinstance(color,str):
            if color in COLOR.__members__:
                self.color=COLOR[color]
            else:
                raise ValueError(f'{color} is not a valid COLOR!')

        self.filled=filled
        self.shape=shape
        self._orient=0

        if x is None:x=parentMaze.rows
        if y is None:y=parentMaze.cols

        self.x=x
        self.y=y
        self.footprints=footprints
        self.parent_maze._agents.append(self)

        if goal==None:
            self.goal=self.parent_maze._goal
        else:
            self.goal=goal
        self._body=[]
        self.position=(self.x,self.y)
        
    @property
    def x(self):
        return self._x

    @x.setter
    def x(self,newX):
        self._x=newX

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self,new_y):
        self._y=new_y
        w=self.parent_maze._cell_width
        x=self.x*w-w+self.parent_maze._LabWidth
        y=self.y*w-w+self.parent_maze._LabWidth
        if self.shape=='square':
            if self.filled:
                self._coord=(y, x,y + w, x + w)
            else:
                self._coord=(y + w/2.5, x + w/2.5,y + w/2.5 +w/4, x + w/2.5 +w/4)
        else:
            self._coord=(y + w/2, x + 3*w/9,y + w/2, x + 3*w/9+w/4)

        if hasattr(self,'_head'):
            if self.footprints is False:
                self.parent_maze._canvas.delete(self._head)
            else:
                if self.shape=='square':
                    self.parent_maze._canvas.itemconfig(self._head, fill=self.color.value[1],outline="")
                    self.parent_maze._canvas.tag_raise(self._head)
                    try:
                        self.parent_maze._canvas.tag_lower(self._head,'ov')
                    except:
                        pass
                    if self.filled:
                        lll=self.parent_maze._canvas.coords(self._head)
                        oldcell=(round(((lll[1]-26)/self.parent_maze._cell_width)+1),round(((lll[0]-26)/self.parent_maze._cell_width)+1))
                        self.parent_maze.redraw_cell(*oldcell,self.parent_maze.theme)
                else:
                    self.parent_maze._canvas.itemconfig(self._head, fill=self.color.value[1])#,outline='gray70')
                    self.parent_maze._canvas.tag_raise(self._head)
                    try:
                        self.parent_maze._canvas.tag_lower(self._head,'ov')
                    except:
                        pass
                self._body.append(self._head)
            if not self.filled or self.shape=='arrow':
                if self.shape=='square':
                    self._head=self.parent_maze._canvas.create_rectangle(*self._coord,fill=self.color.value[0],outline='') #stipple='gray75'
                    try:
                        self.parent_maze._canvas.tag_lower(self._head,'ov')
                    except:
                        pass
                else:
                    self._head=self.parent_maze._canvas.create_line(*self._coord,fill=self.color.value[0],arrow=FIRST,arrowshape=(3/10*w,4/10*w,4/10*w))#,outline=self.color.name)
                    try:
                        self.parent_maze._canvas.tag_lower(self._head,'ov')
                    except:
                        pass
                    o=self._orient%4
                    if o==1:
                        self._RCW()
                        self._orient-=1
                    elif o==3:
                        self._RCCW()
                        self._orient+=1
                    elif o==2:
                        self._RCCW()
                        self._RCCW()
                        self._orient+=2
            else:
                self._head=self.parent_maze._canvas.create_rectangle(*self._coord,fill=self.color.value[0],outline='')#stipple='gray75'
                try:
                    self.parent_maze._canvas.tag_lower(self._head,'ov')
                except:
                        pass
                self.parent_maze.redraw_cell(self.x,self.y,theme=self.parent_maze.theme)
        else:
            self._head=self.parent_maze._canvas.create_rectangle(*self._coord,fill=self.color.value[0],outline='')#stipple='gray75'
            try:
                self.parent_maze._canvas.tag_lower(self._head,'ov')
            except:
                pass
            self.parent_maze.redraw_cell(self.x,self.y,theme=self.parent_maze.theme)

    @property
    def position(self):
        return (self.x,self.y)

    @position.setter
    def position(self,newpos):
        self.x=newpos[0]
        self.y=newpos[1]
        self._position=newpos

    def _RCCW(self):
        def pointNew(p,newOrigin):
            return (p[0]-newOrigin[0],p[1]-newOrigin[1])

        w=self.parent_maze._cell_width
        x=self.x*w-w+self.parent_maze._LabWidth
        y=self.y*w-w+self.parent_maze._LabWidth
        cent=(y+w/2,x+w/2)
        p1=pointNew((self._coord[0],self._coord[1]),cent)
        p2=pointNew((self._coord[2],self._coord[3]),cent)
        p1CW=(p1[1],-p1[0])
        p2CW=(p2[1],-p2[0])
        p1=p1CW[0]+cent[0],p1CW[1]+cent[1]
        p2=p2CW[0]+cent[0],p2CW[1]+cent[1]
        self._coord=(*p1,*p2)  
        self.parent_maze._canvas.coords(self._head,*self._coord)
        self._orient=(self._orient-1)%4
 
        
    def _RCW(self):
        def pointNew(p,new_origin):
            return (p[0]-new_origin[0],p[1]-new_origin[1])

        w=self.parent_maze._cell_width
        x=self.x*w-w+self.parent_maze._LabWidth
        y=self.y*w-w+self.parent_maze._LabWidth

        cent=(y+w/2,x+w/2)

        p1=pointNew((self._coord[0],self._coord[1]),cent)
        p2=pointNew((self._coord[2],self._coord[3]),cent)

        p1CW=(-p1[1],p1[0])
        p2CW=(-p2[1],p2[0])
        p1=p1CW[0]+cent[0],p1CW[1]+cent[1]
        p2=p2CW[0]+cent[0],p2CW[1]+cent[1]

        self._coord=(*p1,*p2)  
        self.parent_maze._canvas.coords(self._head,*self._coord)
        self._orient=(self._orient+1)%4

    def move_right(self):
        if self.parent_maze.maze_map[self.x,self.y]['E']==True:
            self.y=self.y+1

    def move_left(self):
        if self.parent_maze.maze_map[self.x,self.y]['W']==True:
            self.y=self.y-1

    def move_up(self):
        if self.parent_maze.maze_map[self.x,self.y]['N']==True:
            self.x=self.x-1
            self.y=self.y

    def move_down(self):
        if self.parent_maze.maze_map[self.x,self.y]['S']==True:
            self.x=self.x+1
            self.y=self.y


class Maze:
    def __init__(self, rows=10, cols=10):
        self.rows=rows
        self.cols=cols
        self.maze_map={}
        self.grid=[]
        self.path={} 
        self._cell_width=50  
        self._win=None 
        self._canvas=None
        self._agents=[]
        self.markCells=[]

    @property
    def grid(self):
        return self._grid

    @grid.setter        
    def grid(self, n):
        self._grid=[]
        y=0
        for _ in range(self.cols):
            x = 1
            y = 1+y
            for _ in range(self.rows):
                self.grid.append((x,y))
                self.maze_map[x,y]={'E':0,'W':0,'N':0,'S':0}
                x = x + 1 

    def open_east(self,x, y):
        self.maze_map[x,y]['E']=1
        if y+1<=self.cols:
            self.maze_map[x,y+1]['W']=1

    def open_west(self,x, y):
        self.maze_map[x,y]['W']=1
        if y-1>0:
            self.maze_map[x,y-1]['E']=1

    def open_north(self,x, y):
        self.maze_map[x,y]['N']=1
        if x-1>0:
            self.maze_map[x-1,y]['S']=1

    def open_south(self,x, y):
        self.maze_map[x,y]['S']=1
        if x+1<=self.rows:
            self.maze_map[x+1,y]['N']=1
    
    def create_maze(self,x=1,y=1,pattern=None,loop_percent=0,save_maze=False,load_maze=None,theme:COLOR=COLOR.dark):
        _stack=[]
        _closed=[]
        self.theme=theme
        self._goal=(x,y)

        if(isinstance(theme,str)):
            if(theme in COLOR.__members__):
                self.theme=COLOR[theme]
            else:
                raise ValueError(f'{theme} is not a valid theme COLOR!')

        def blocked_neighbours(cell):
            n=[]
            for d in self.maze_map[cell].keys():
                if self.maze_map[cell][d]==0:
                    if d=='E' and (cell[0],cell[1]+1) in self.grid:
                        n.append((cell[0],cell[1]+1))
                    elif d=='W' and (cell[0],cell[1]-1) in self.grid:
                        n.append((cell[0],cell[1]-1))
                    elif d=='N' and (cell[0]-1,cell[1]) in self.grid:
                        n.append((cell[0]-1,cell[1]))
                    elif d=='S' and (cell[0]+1,cell[1]) in self.grid:
                        n.append((cell[0]+1,cell[1]))
            return n

        def remove_wall_in_between(cell1,cell2):
            if cell1[0]==cell2[0]:
                if cell1[1]==cell2[1]+1:
                    self.maze_map[cell1]['W']=1
                    self.maze_map[cell2]['E']=1
                else:
                    self.maze_map[cell1]['E']=1
                    self.maze_map[cell2]['W']=1
            else:
                if cell1[0]==cell2[0]+1:
                    self.maze_map[cell1]['N']=1
                    self.maze_map[cell2]['S']=1
                else:
                    self.maze_map[cell1]['S']=1
                    self.maze_map[cell2]['N']=1

        def is_cyclic(cell1, cell2):
            ans=False
            if cell1[0]==cell2[0]:
                if cell1[1]>cell2[1]: cell1,cell2=cell2,cell1
                if self.maze_map[cell1]['S']==1 and self.maze_map[cell2]['S']==1:
                    if (cell1[0]+1,cell1[1]) in self.grid and self.maze_map[(cell1[0]+1,cell1[1])]['E']==1:
                        ans= True
                if self.maze_map[cell1]['N']==1 and self.maze_map[cell2]['N']==1:
                    if (cell1[0]-1,cell1[1]) in self.grid and self.maze_map[(cell1[0]-1,cell1[1])]['E']==1:
                        ans= True
            else:
                if cell1[0]>cell2[0]: cell1,cell2=cell2,cell1
                if self.maze_map[cell1]['E']==1 and self.maze_map[cell2]['E']==1:
                    if (cell1[0],cell1[1]+1) in self.grid and self.maze_map[(cell1[0],cell1[1]+1)]['S']==1:
                        ans= True
                if self.maze_map[cell1]['W']==1 and self.maze_map[cell2]['W']==1:
                    if (cell1[0],cell1[1]-1) in self.grid and self.maze_map[(cell1[0],cell1[1]-1)]['S']==1:
                        ans= True
            return ans

        def get_path(cell):
            frontier = deque()
            frontier.append(cell)
            path = {}
            visited = {(self.rows,self.cols)}

            while len(frontier) > 0:
                cell = frontier.popleft()
                if self.maze_map[cell]['W'] and (cell[0],cell[1]-1) not in visited:
                    nextCell = (cell[0],cell[1]-1)
                    path[nextCell] = cell
                    frontier.append(nextCell)
                    visited.add(nextCell)
                if self.maze_map[cell]['S'] and (cell[0]+1,cell[1]) not in visited:    
                    nextCell = (cell[0]+1,cell[1])
                    path[nextCell] = cell
                    frontier.append(nextCell)
                    visited.add(nextCell)
                if self.maze_map[cell]['E'] and (cell[0],cell[1]+1) not in visited:
                    nextCell = (cell[0],cell[1]+1)
                    path[nextCell] = cell
                    frontier.append(nextCell)
                    visited.add(nextCell)
                if self.maze_map[cell]['N'] and (cell[0]-1,cell[1]) not in visited:
                    nextCell = (cell[0]-1,cell[1])
                    path[nextCell] = cell
                    frontier.append(nextCell)
                    visited.add(nextCell)
            fwdPath={}
            cell=self._goal

            while cell!=(self.rows,self.cols):
                try:
                    fwdPath[path[cell]]=cell
                    cell=path[cell]
                except:
                    print('Path to goal not found!')
                    return
            return fwdPath

        # if maze is to be generated randomly
        if not load_maze:
            _stack.append((x,y))
            _closed.append((x,y))
            biasLength=2 # if pattern is 'v' or 'h'
            if(pattern is not None and pattern.lower()=='h'):
                biasLength=max(self.cols//10,2)
            if(pattern is not None and pattern.lower()=='v'):
                biasLength=max(self.rows//10,2)
            bias=0

            while len(_stack) > 0:
                cell = []
                bias+=1
                if(x , y +1) not in _closed and (x , y+1) in self.grid:
                    cell.append("E")
                if (x , y-1) not in _closed and (x , y-1) in self.grid:
                    cell.append("W")
                if (x+1, y ) not in _closed and (x+1 , y ) in self.grid:
                    cell.append("S")
                if (x-1, y ) not in _closed and (x-1 , y) in self.grid:
                    cell.append("N") 
                if len(cell) > 0:    
                    if pattern is not None and pattern.lower()=='h' and bias<=biasLength:
                        if('E' in cell or 'W' in cell):
                            if 'S' in cell:cell.remove('S')
                            if 'N' in cell:cell.remove('N')
                    elif pattern is not None and pattern.lower()=='v' and bias<=biasLength:
                        if('N' in cell or 'S' in cell):
                            if 'E' in cell:cell.remove('E')
                            if 'W' in cell:cell.remove('W')
                    else:
                        bias=0
                    current_cell = (random.choice(cell))
                    if current_cell == "E":
                        self.open_east(x,y)
                        self.path[x, y+1] = x, y
                        y = y + 1
                        _closed.append((x, y))
                        _stack.append((x, y))

                    elif current_cell == "W":
                        self.open_west(x, y)
                        self.path[x , y-1] = x, y
                        y = y - 1
                        _closed.append((x, y))
                        _stack.append((x, y))

                    elif current_cell == "N":
                        self.open_north(x, y)
                        self.path[(x-1 , y)] = x, y
                        x = x - 1
                        _closed.append((x, y))
                        _stack.append((x, y))

                    elif current_cell == "S":
                        self.open_south(x, y)
                        self.path[(x+1 , y)] = x, y
                        x = x + 1
                        _closed.append((x, y))
                        _stack.append((x, y))

                else:
                    x, y = _stack.pop()

            ## Multiple Path Loops
            if loop_percent!=0:
                
                x,y=self.rows,self.cols
                pathCells=[(x,y)]
                while x!=self.rows or y!=self.cols:
                    x,y=self.path[(x,y)]
                    pathCells.append((x,y))
                notPathCells=[i for i in self.grid if i not in pathCells]
                random.shuffle(pathCells)
                random.shuffle(notPathCells)
                pathLength=len(pathCells)
                notPathLength=len(notPathCells)
                count1,count2=pathLength/3*loop_percent/100,notPathLength/3*loop_percent/100
                
                #remove blocks from shortest path cells
                count=0
                i=0
                while count<count1: #these many blocks to remove
                    if len(blocked_neighbours(pathCells[i]))>0:
                        cell=random.choice(blocked_neighbours(pathCells[i]))
                        if not is_cyclic(cell,pathCells[i]):
                            remove_wall_in_between(cell,pathCells[i])
                            count+=1
                        i+=1
                            
                    else:
                        i+=1
                    if i==len(pathCells):
                        break
                #remove blocks from outside shortest path cells
                if len(notPathCells)>0:
                    count=0
                    i=0
                    while count<count2: #these many blocks to remove
                        if len(blocked_neighbours(notPathCells[i]))>0:
                            cell=random.choice(blocked_neighbours(notPathCells[i]))
                            if not is_cyclic(cell,notPathCells[i]):
                                remove_wall_in_between(cell,notPathCells[i])
                                count+=1
                            i+=1
                                
                        else:
                            i+=1
                        if i==len(notPathCells):
                            break
                self.path=get_path((self.rows,self.cols))
        else:
            # Load maze from CSV file
            with open(load_maze,'r') as f:
                last=list(f.readlines())[-1]
                c=last.split(',')
                c[0]=int(c[0].lstrip('"('))
                c[1]=int(c[1].rstrip(')"'))
                self.rows=c[0]
                self.cols=c[1]
                self.grid=[]

            with open(load_maze,'r') as f:
                r=csv.reader(f)
                next(r)
                for i in r:
                    c=i[0].split(',')
                    c[0]=int(c[0].lstrip('('))
                    c[1]=int(c[1].rstrip(')'))
                    self.maze_map[tuple(c)]={'E':int(i[1]),'W':int(i[2]),'N':int(i[3]),'S':int(i[4])}
            self.path=get_path((self.rows,self.cols))
        self.draw_maze(self.theme)

        # DEFAULT AGENT SETTINGS
        Agent(self,*self._goal,shape='square',filled=True,color=COLOR.green)

        if save_maze:
            dt_string = datetime.datetime.now().strftime("%Y-%m-%d--%H-%M-%S")
            with open(f'maze--{dt_string}.csv','w',newline='') as f:
                writer=csv.writer(f)
                writer.writerow(['  cell  ','E','W','N','S'])
                for k,v in self.maze_map.items():
                    entry=[k]
                    for i in v.values():
                        entry.append(i)
                    writer.writerow(entry)
                f.seek(0, os.SEEK_END)
                f.seek(f.tell()-2, os.SEEK_SET)
                f.truncate()

    def draw_maze(self, theme):
        self._LabWidth=26 # Space from the top for Labels
        self._win=Tk()
        self._win.state('zoomed')
        self._win.title('A* Maze')
        
        scr_width=self._win.winfo_screenwidth()
        scr_height=self._win.winfo_screenheight()

        self._win.geometry(f"{scr_width}x{scr_height}+0+0")
        self._canvas = Canvas(width=scr_width, height=scr_height, bg=theme.value[0]) # 0,0 is top left corner
        self._canvas.pack(expand=YES, fill=BOTH)
        # Some calculations for calculating the width of the maze cell
        k=3.25
        if self.rows>=95 and self.cols>=95:
            k=0
        elif self.rows>=80 and self.cols>=80:
            k=1
        elif self.rows>=70 and self.cols>=70:
            k=1.5
        elif self.rows>=50 and self.cols>=50:
            k=2
        elif self.rows>=35 and self.cols>=35:
            k=2.5
        elif self.rows>=22 and self.cols>=22:
            k=3
        self._cell_width=round(min(((scr_height-self.rows-k*self._LabWidth)/(self.rows)),((scr_width-self.cols-k*self._LabWidth)/(self.cols)),90),3)
        
        # Creating Maze lines
        if self._win is not None:
            if self.grid is not None:
                for cell in self.grid:
                    x,y=cell
                    w=self._cell_width
                    x=x*w-w+self._LabWidth
                    y=y*w-w+self._LabWidth
                    if self.maze_map[cell]['E']==False:
                        self._canvas.create_line(y + w, x, y + w, x + w,width=2,fill=theme.value[1],tag='line')
                    if self.maze_map[cell]['W']==False:
                        self._canvas.create_line(y, x, y, x + w,width=2,fill=theme.value[1],tag='line')
                    if self.maze_map[cell]['N']==False:
                        self._canvas.create_line(y, x, y + w, x,width=2,fill=theme.value[1],tag='line')
                    if self.maze_map[cell]['S']==False:
                        self._canvas.create_line(y, x + w, y + w, x + w,width=2,fill=theme.value[1],tag='line')

    def redraw_cell(self,x,y,theme):
        w=self._cell_width
        cell=(x,y)
        x=x*w-w+self._LabWidth
        y=y*w-w+self._LabWidth
        if self.maze_map[cell]['E']==False:
            self._canvas.create_line(y + w, x, y + w, x + w,width=2,fill=theme.value[1])
        if self.maze_map[cell]['W']==False:
            self._canvas.create_line(y, x, y, x + w,width=2,fill=theme.value[1])
        if self.maze_map[cell]['N']==False:
            self._canvas.create_line(y, x, y + w, x,width=2,fill=theme.value[1])
        if self.maze_map[cell]['S']==False:
            self._canvas.create_line(y, x + w, y + w, x + w,width=2,fill=theme.value[1])

    _tracePathList=[]
    def trace_path_single(self,a,p,kill,show_marked,delay):
        
        def kill_agent(a):
            for i in range(len(a._body)):
                self._canvas.delete(a._body[i])
            self._canvas.delete(a._head) 

        w=self._cell_width
        if((a.x,a.y) in self.markCells and show_marked):
            w=self._cell_width
            x=a.x*w-w+self._LabWidth
            y=a.y*w-w+self._LabWidth
            self._canvas.create_oval(y + w/2.5+w/20, x + w/2.5+w/20,y + w/2.5 +w/4-w/20, x + w/2.5 +w/4-w/20,fill='red',outline='red',tag='ov')
            self._canvas.tag_raise('ov')
       
        if (a.x,a.y)==(a.goal):
            del Maze._tracePathList[0][0][a]
            if Maze._tracePathList[0][0]=={}:
                del Maze._tracePathList[0]
                if len(Maze._tracePathList)>0:
                    self.trace_path(Maze._tracePathList[0][0],kill=Maze._tracePathList[0][1],delay=Maze._tracePathList[0][2])
            if kill:
                self._win.after(300, kill_agent,a)         
            return

        # If path is provided as Dictionary
        if(type(p)==dict):
            if(len(p)==0):
                del Maze._tracePathList[0][0][a]
                return
            if a.shape=='arrow':
                old=(a.x,a.y)
                new=p[(a.x,a.y)]
                o=a._orient
                
                if old!=new:
                    if old[0]==new[0]:
                        if old[1]>new[1]:
                            mov=3#'W' #3
                        else:
                            mov=1#'E' #1
                    else:
                        if old[0]>new[0]:
                            mov=0#'N' #0

                        else:
                            mov=2#'S' #2
                    if mov-o==2:
                        a._RCW()

                    if mov-o==-2:
                        a._RCW()
                    if mov-o==1:
                        a._RCW()
                    if mov-o==-1:
                        a._RCCW()
                    if mov-o==3:
                        a._RCCW()
                    if mov-o==-3:
                        a._RCW()
                    if mov==o:
                        a.x,a.y=p[(a.x,a.y)]
                else:
                    del p[(a.x,a.y)]
            else:    
                a.x,a.y=p[(a.x,a.y)]

        # If path is provided as String
        if (type(p)==str):
            if(len(p)==0):
                del Maze._tracePathList[0][0][a]
                if Maze._tracePathList[0][0]=={}:
                    del Maze._tracePathList[0]
                    if len(Maze._tracePathList)>0:
                        self.trace_path(Maze._tracePathList[0][0],kill=Maze._tracePathList[0][1],delay=Maze._tracePathList[0][2])
                if kill:
                    
                    self._win.after(300, kill_agent,a)         
                return
            if a.shape=='arrow':
                old=(a.x,a.y)
                new=p[0]
                o=a._orient
                if new=='N': mov=0
                elif new=='E': mov=1
                elif new=='S': mov=2
                elif new=='W': mov=3
                
                if mov-o==2:
                    a._RCW()

                if mov-o==-2:
                    a._RCW()
                if mov-o==1:
                    a._RCW()
                if mov-o==-1:
                    a._RCCW()
                if mov-o==3:
                    a._RCCW()
                if mov-o==-3:
                    a._RCW()
            if a.shape=='square' or mov==o:    
                move=p[0]
                if move=='E':
                    if a.y+1<=self.cols:
                        a.y+=1
                elif move=='W':
                    if a.y-1>0:
                        a.y-=1
                elif move=='N':
                    if a.x-1>0:
                        a.x-=1
                        a.y=a.y
                elif move=='S':
                    if a.x+1<=self.rows:
                        a.x+=1
                        a.y=a.y
                elif move=='C':
                    a._RCW()
                elif move=='A':
                    a._RCCW()
                p=p[1:]

        # If path is provided as List
        if (type(p)==list):
            if(len(p)==0):
                del Maze._tracePathList[0][0][a]
                if Maze._tracePathList[0][0]=={}:
                    del Maze._tracePathList[0]
                    if len(Maze._tracePathList)>0:
                        self.trace_path(Maze._tracePathList[0][0],kill=Maze._tracePathList[0][1],delay=Maze._tracePathList[0][2])
                if kill:                    
                    self._win.after(300, kill_agent,a)  
                return
            if a.shape=='arrow':
                old=(a.x,a.y)
                new=p[0]
                o=a._orient
                
                if old!=new:
                    if old[0]==new[0]:
                        if old[1]>new[1]:
                            mov=3#'W' #3
                        else:
                            mov=1#'E' #1
                    else:
                        if old[0]>new[0]:
                            mov=0#'N' #0

                        else:
                            mov=2#'S' #2
                    if mov-o==2:
                        a._RCW()

                    elif mov-o==-2:
                        a._RCW()
                    elif mov-o==1:
                        a._RCW()
                    elif mov-o==-1:
                        a._RCCW()
                    elif mov-o==3:
                        a._RCCW()
                    elif mov-o==-3:
                        a._RCW()
                    elif mov==o:
                        a.x,a.y=p[0]
                        del p[0]
                else:
                    del p[0]
            else:    
                a.x,a.y=p[0]
                del p[0]

        self._win.after(delay, self.trace_path_single,a,p,kill,show_marked,delay)    

    def trace_path(self,d,kill=False,delay=300,show_marked=False):
        self._tracePathList.append((d,kill,delay))
        if Maze._tracePathList[0][0]==d: 
            for a,p in d.items():
                if a.goal!=(a.x,a.y) and len(p)!=0:
                    self.trace_path_single(a,p,kill,show_marked,delay)

    def run(self):
        self._win.mainloop()