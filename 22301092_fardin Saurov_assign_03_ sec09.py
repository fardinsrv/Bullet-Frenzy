from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math

GAME_STATE_RUNNING = 1
GAME_STATE_OVER = 0
game_state = GAME_STATE_RUNNING

camera_angle = 45.0 
camera_pos = (0, 500, 500)
camera_height = 500.0
WALL_HEIGHT = 100  

fovY = 120  
GRID_LENGTH = 1200 
rand_var = 423


first_person = False        
cheat_mode = False   
cheat_vision = False         

player_xy = [0.0, 0.0]    
player_height = 80.0
gun_angle = 0.0       
walk_step = 16.0
turn_step = 4.0
gun_len = 160.0           

lives = 5
score = 0
missed = 0

bullets = []          
BULLET_SPEED = 40.0
BULLET_COOLDOWN = 0          
mouse_down = False           

ENEMY_COUNT = 5
enemies = []                 

booted = False                

def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(1,1,1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    

    gluOrtho2D(0, 1000, 0, 800)  # left, right, bottom, top

    
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))
    

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_shapes():
    return

def clamp(v, lo, hi):
    return lo if v < lo else hi if v > hi else v


def frand(a, b):
    global rand_var
    rand_var = (rand_var * 1664525 + 1013904223) & 0xffffffff
    t = (rand_var & 0xffffff) / float(0xffffff)
    return a + (b - a) * t

def spawn_enemy():
    r = GRID_LENGTH * 0.75
    ex, ey = frand(-r, r), frand(-r, r)
    if (ex - player_xy[0])**2 + (ey - player_xy[1])**2 < 200**2:
        ex += 250; ey -= 250
    return {'x': ex, 'y': ey, 'e_z': frand(0, 6.283)}

def reset_game():
    global lives, score, missed, bullets, enemies, game_state
    global player_xy, gun_angle, BULLET_COOLDOWN, first_person, cheat_mode, cheat_vision, mouse_down
    lives, score, missed = 5, 0, 0
    bullets, enemies = [], [spawn_enemy() for _ in range(ENEMY_COUNT)]
    BULLET_COOLDOWN = 0
    mouse_down = False
    player_xy[:] = [0.0, 0.0]
    gun_angle = 0.0
    first_person = False
    cheat_mode = False
    cheat_vision = False
    game_state = GAME_STATE_RUNNING

def fire_bullet():
    global bullets, BULLET_COOLDOWN
    if game_state != GAME_STATE_RUNNING or BULLET_COOLDOWN > 0:
        return
    ang = math.radians(gun_angle)
    sx = player_xy[0] + math.cos(ang) * (gun_len + 60)
    sy = player_xy[1] + math.sin(ang) * (gun_len + 60)
    bullets.append({'x': sx, 'y': sy, 'ang': gun_angle})
    BULLET_COOLDOWN = 6  # frames

def draw_bullets():
    for b in bullets:
        glPushMatrix()
        glTranslatef(b['x'], b['y'], 40)
        glColor3f(1.0, 0.0, 0.0)
        glScalef(0.6, 0.6, 0.6)
        glutSolidCube(20)
        glPopMatrix()

def draw_enemy(e):
    s = 0.5 + 0.125 * math.sin(e['e_z'])  #choto boro korar jonno
    glPushMatrix()
    glTranslatef(e['x'], e['y'], 40)
    glColor3f(1.0, 0.2, 0.2)             # body
    gluSphere(gluNewQuadric(), 45 * s, 16, 12) 
    glTranslatef(0, 0, 25 * s + 25 * s)  # head 
    glColor3f(0.0, 0.0, 0.0)
    gluSphere(gluNewQuadric(), 10 * s, 12, 10) # Reduced radius
    glPopMatrix()

def draw_enemies():
    for e in enemies:
        draw_enemy(e)

def draw_player():
    glPushMatrix()
    glTranslatef(player_xy[0], player_xy[1], 0) # current pos
    if game_state == GAME_STATE_OVER:
        glRotatef(-90, 1, 0, 0)  # lie down
    glRotatef(gun_angle, 0, 0, 1)  


    glPushMatrix() #body
    glTranslatef(0, 0, 40) 
    glColor3f(0.2, 0.55, 0.2)
    glScalef(0.5, 0.3, 0.6) 
    glutSolidCube(120)
    glPopMatrix()

    glPushMatrix() #matha
    glTranslatef(0, 0, 80) 
    glColor3f(0.0, 0.0, 0.0)
    gluSphere(gluNewQuadric(), 20, 16, 12)
    glPopMatrix()


    glPushMatrix() #gun head
    glTranslatef(-35, 0, 55) 
    glRotatef(90, 1, 0, 0)
    glColor3f(0.85, 0.85, 0.85)
    gluCylinder(gluNewQuadric(), 9, 9, 35, 10, 1) 
    glPopMatrix()

    glPushMatrix() #gun tail
    glTranslatef(35, 0, 55)
    glRotatef(90, 1, 0, 0)
    glColor3f(0.85, 0.85, 0.85)
    gluCylinder(gluNewQuadric(), 9, 9, 35, 10, 1)
    glPopMatrix()


    glPushMatrix() 
    glTranslatef(0, 30, 55) 
    glColor3f(0.6, 0.6, 0.6)
    glScalef(0.5, 1.8, 0.2)
    glutSolidCube(40)
    glPopMatrix()

    glPushMatrix() #gun
    glTranslatef(0, 60, 55) 
    glColor3f(0.4, 0.4, 0.4)
    glScalef(0.3, 3.0, 0.3) 
    glutSolidCube(30)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(-17.5, -5, 20) 
    glColor3f(0.0, 0.0, 0.6)
    glScalef(0.3, 0.3, 0.7)
    glutSolidCube(70)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(17.5, -5, 20)
    glColor3f(0.0, 0.0, 0.6)
    glScalef(0.3, 0.3, 0.7) 
    glutSolidCube(70)
    glPopMatrix()
    glPopMatrix()

def applyFirstPersonCamera():
    ang = math.radians(gun_angle)
    dx, dy = math.cos(ang), math.sin(ang)

    ex = player_xy[0] - dx * 40
    ey = player_xy[1] - dy * 40
    ez = 130

    ax = player_xy[0] + dx * 200
    ay = player_xy[1] + dy * 200
    az = ez

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(ex, ey, ez, 
              ax, ay, az,
              0, 0, 1)

def auto_cheat_actions():
    if not cheat_mode or game_state != GAME_STATE_RUNNING:
        return
    global gun_angle
    gun_angle = (gun_angle + 3.0) % 360.0

    # fire when aim lines up with any enemy (small angular error)
    best = 999.0
    for e in enemies:
        a = math.degrees(math.atan2(e['y'] - player_xy[1], e['x'] - player_xy[0]))
        if a < 0: a += 360
        d = abs(((a - gun_angle + 180) % 360) - 180)
        if d < best: best = d
    if best < 6.0:
        fire_bullet()

def update_logic(value):
    global booted, rand_var
    if not booted:
        reset_game()
        booted = True
    
    rand_var += 1
    auto_cheat_actions()
    update_world()
    

    glutTimerFunc(1000 // 60, update_logic, 0)
    
def update_world():
    global bullets, enemies, score, missed, lives, game_state, BULLET_COOLDOWN, fovY, mouse_down

    if BULLET_COOLDOWN > 0:
        BULLET_COOLDOWN -= 1
    

    if mouse_down:
        fire_bullet()


    still = []
    for b in bullets:
        ang = math.radians(b['ang'])
        b['x'] += math.cos(ang) * BULLET_SPEED
        b['y'] += math.sin(ang) * BULLET_SPEED
        if abs(b['x']) > GRID_LENGTH or abs(b['y']) > GRID_LENGTH:
            missed += 1
        else:
            still.append(b)
    bullets = still

    for e in enemies:
        dx = player_xy[0] - e['x']; dy = player_xy[1] - e['y']
        d = math.sqrt(dx * dx + dy * dy) + 1e-6
        step = 0.1 
        e['x'] += dx / d * step
        e['y'] += dy / d * step
        e['e_z'] += 0.12


    for e in enemies:
        for b in list(bullets):
            dx = b['x'] - e['x']; dy = b['y'] - e['y']
            if dx * dx + dy * dy < 55 * 55:
                score += 1
                bullets.remove(b)
                e.update(spawn_enemy())
                break

    # enemyplayer col
    for e in enemies:
        dx = player_xy[0] - e['x']; dy = player_xy[1] - e['y']
        if dx * dx + dy * dy < 70 * 70 and game_state == GAME_STATE_RUNNING:
            lives -= 1
            e.update(spawn_enemy())

    # game_sesh
    if lives <= 0 or missed >= 10:
        game_state = GAME_STATE_OVER

    fovY = 100 if (cheat_mode and cheat_vision and first_person) else 120

def keyboardListener(key, x, y):
    global gun_angle, player_xy, cheat_mode, cheat_vision
    global lives, score, missed

    if key == b'w' or key == b'W' and game_state == GAME_STATE_RUNNING:
        ang = math.radians(gun_angle)
        player_xy[0] += math.cos(ang) * walk_step
        player_xy[1] += math.sin(ang) * walk_step
    
    if key == b's' or key == b'S' and game_state == GAME_STATE_RUNNING:
        ang = math.radians(gun_angle)
        player_xy[0] -= math.cos(ang) * walk_step
        player_xy[1] -= math.sin(ang) * walk_step
    
    if key == b'a' or key == b'A':
        gun_angle = (gun_angle - turn_step) % 360.0
    
    if key == b'd' or key == b'D':
        gun_angle = (gun_angle + turn_step) % 360.0

    if key == b'c':
        cheat_mode = not cheat_mode
    
    if key == b'v':
        cheat_vision = not cheat_vision
    
    if key == b'r':
        reset_game()

    # keep player inside the walls
    player_xy[0] = clamp(player_xy[0], -GRID_LENGTH + 60, GRID_LENGTH - 60)
    player_xy[1] = clamp(player_xy[1], -GRID_LENGTH + 60, GRID_LENGTH - 60)

def specialKeyListener(key, x, y):

    global camera_pos, camera_angle, camera_height
    

    if key == GLUT_KEY_UP:
        camera_height += 5 
    

    if key == GLUT_KEY_DOWN:
        camera_height -= 5

        camera_angle -= 1.0  
        if camera_angle < 0:
            camera_angle += 360
    
    if key == GLUT_KEY_RIGHT:
        camera_angle += 1.0 
        if camera_angle > 360:
            camera_angle -= 360 

    if key == GLUT_KEY_LEFT:
        camera_angle -= 1.0  
        if camera_angle < 0:
            camera_angle += 360        


def mouseListener(button, state, x, y):
    global first_person, mouse_down

    if button == GLUT_LEFT_BUTTON:
        if state == GLUT_DOWN:
            mouse_down = True
        elif state == GLUT_UP:
            mouse_down = False
    
    if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        first_person = not first_person

def setupCamera():
    """
    Configures the camera for third-person (top-down style) view.
    Camera now follows the player instead of being fixed at origin.
    """
    global camera_angle, camera_height, fovY

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fovY, 1.25, 0.1, 2000)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

 
    d = 400  
    x = player_xy[0] + d * math.cos(math.radians(camera_angle))
    y = player_xy[1] + d * math.sin(math.radians(camera_angle))
    z = camera_height

    # Look at player
    gluLookAt(x, y, z,
              player_xy[0], player_xy[1], 0,
              0, 0, 1)

def idle():

    glutPostRedisplay()

def showScreen():
    """
    Display function to render the game scene:
    - Clears the screen and sets up the camera.
    - Draws everything on the screen.
    """
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT) 
    glViewport(0, 0, 1000, 800) 

    if first_person:
        applyFirstPersonCamera()
    else:
        setupCamera()

    glPointSize(20)
    glBegin(GL_POINTS)
    glVertex3f(0, 0, 0)
    glEnd()

    # grid
    glBegin(GL_QUADS)
    for i in range(-GRID_LENGTH, GRID_LENGTH, 100):
        for j in range(-GRID_LENGTH, GRID_LENGTH, 100):
            if ((i // 100) + (j // 100)) % 2 == 0:
                glColor3f(1.0, 1.0, 1.0)  # White
            else:
                glColor3f(0.7, 0.5, 0.95)  # Purple
            glVertex3f(i, j, 0)
            glVertex3f(i + 100, j, 0)
            glVertex3f(i + 100, j + 100, 0)
            glVertex3f(i, j + 100, 0)
    glEnd()

    # Walls 
    glBegin(GL_QUADS)
    glColor3f(0.0, 0.0, 1.0)
    glVertex3f(-GRID_LENGTH, -GRID_LENGTH, 0)
    glVertex3f(-GRID_LENGTH, GRID_LENGTH, 0)
    glVertex3f(-GRID_LENGTH, GRID_LENGTH, WALL_HEIGHT)
    glVertex3f(-GRID_LENGTH, -GRID_LENGTH, WALL_HEIGHT)

    glColor3f(0.0, 1.0, 0.0)
    glVertex3f(GRID_LENGTH, -GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, GRID_LENGTH, WALL_HEIGHT)
    glVertex3f(GRID_LENGTH, -GRID_LENGTH, WALL_HEIGHT)

    glColor3f(1.0, 0.0, 0.0)
    glVertex3f(-GRID_LENGTH, -GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, -GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, -GRID_LENGTH, WALL_HEIGHT)
    glVertex3f(-GRID_LENGTH, -GRID_LENGTH, WALL_HEIGHT)

    glColor3f(1.0, 1.0, 0.0)
    glVertex3f(-GRID_LENGTH, GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, GRID_LENGTH, WALL_HEIGHT)
    glVertex3f(-GRID_LENGTH, GRID_LENGTH, WALL_HEIGHT)
    glEnd()


    draw_player()
    draw_enemies()
    draw_bullets()

    draw_text(10, 770, f"Player Life Remaining: {lives}")
    draw_text(10, 740, f"Game Score: {score}")
    draw_text(10, 710, f"Player Bullet Missed: {missed}")
    if game_state == GAME_STATE_OVER:
        draw_text(420, 720, "holaaa ! GAME OVER  -  Press R to Restart")

    glutSwapBuffers()

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)  # Double buffering, RGB color, depth test
    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(0, 0) 
    wind = glutCreateWindow(b"Fardin  Saurov - 22301092 - Assignment 3") 
    glEnable(GL_DEPTH_TEST)
    glClearColor(0.0, 0.0, 0.0, 1.0)  

    glutDisplayFunc(showScreen)  
    glutKeyboardFunc(keyboardListener)  
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle) 
    glutTimerFunc(0, update_logic, 0) 

    glutMainLoop() 

if __name__ == "__main__":
    main()