import atexit
import json
import os
from datetime import datetime
import random

import pygame

import assetsutils
import textutils
import utils
from vector2 import Vector


class Game:

    @staticmethod
    def create_grid(size_x, size_y, x_spacing, y_spacing, rows, cols):
        rectangles = []
        for row in range(rows):
            r = []
            for col in range(cols):
                # Calculate the position of the current rectangle
                x_pos = (col + 1) * x_spacing + col * size_x
                y_pos = (row + 1) * y_spacing + row * size_y

                new_rect = {'x': x_pos, 'y': y_pos, "r": pygame.Rect(x_pos, y_pos, size_x, size_y)}
                r.append(new_rect)
            rectangles.append(r)
        return rectangles
    
    @staticmethod
    def copymove(r: pygame.Rect, offset: list):
        return pygame.Rect(r.x+offset[0], r.y+offset[1], r.width, r.height)

    def loopvec(self, vec: Vector):
        if vec.x < 0:
            vec.x = self.gridmeta["cols"]-1
        if vec.y < 0:
            vec.y = self.gridmeta["rows"]-1
        if vec.x >= self.gridmeta["cols"]:
            vec.x = 0
        if vec.y >= self.gridmeta["rows"]:
            vec.y = 0

    def remake_bg(self):
        self.bg_surf = pygame.Surface(self.window_size)
        for i in range(self.window_size[1]//self.bg_px_s+1):
            for j in range(self.window_size[0]//self.bg_px_s+1):
                x = j*self.bg_px_s
                y = i*self.bg_px_s
                r = pygame.Rect(x, y, self.bg_px_s, self.bg_px_s)
                pygame.draw.rect(self.bg_surf, utils.random_chromatic(50), r)
        return self.bg_surf
    
    def get_field(self) -> pygame.Surface:
        srf = pygame.Surface(self.window_size, pygame.SRCALPHA)
        w = 0
        h = 0
        for row in self.field:
            for col in row:
                r: pygame.Rect = col["r"]
                w = max(w, r.bottomright[0]+self.gridmeta["sp_x"])
                h = max(h, r.bottomright[1]+self.gridmeta["sp_y"])
                # srf.blit(self.platform_sprites[0], r)
                pygame.draw.rect(srf, (155, 52, 235), self.copymove(r, [4, 4]))
                pygame.draw.rect(srf, (155, 52, 235), self.copymove(r, [2, 2]))
                pygame.draw.rect(srf, (235, 52, 161), r)
                o = 10
                pygame.draw.rect(srf, (158, 36, 122), pygame.Rect(r.x+o, r.y+o, r.width-o*2, r.height-o*2), 3)
                o = 15
                pygame.draw.rect(srf, (158, 36, 122), pygame.Rect(r.x+o, r.y+o, r.width-o*2, r.height-o*2), 3)
        ret = pygame.Surface([w, h], pygame.SRCALPHA)
        ret.blit(srf, [0, 0])
        return ret
    
    def __init__(self):
        atexit.register(self.at_exit)
        pygame.init()
        pygame.display.set_caption("Crystal speedrun")
        pygame.display.set_icon(assetsutils.get_image(assetsutils.assets_folder+os.sep+"icon.png"))
        self.running = False
        self.screen = None
        self.m_info = pygame.display.Info()
        self.fullscreen = False
        self.window_size = (800, 800)
        self.original_size = self.window_size
        self.screen = pygame.display.set_mode(self.window_size, pygame.RESIZABLE)
        self.size_ratio = [1.0, 1.0]
        self.tick = 0
        self.clock = pygame.time.Clock()
        self.main_font = assetsutils.assets_folder+os.sep+"font.ttf"
        loading = textutils.render("Loading..", int(50*self.size_ratio[1]), self.main_font, (51, 255, 177), file=True)
        self.screen.blit(loading, [self.screen.get_size()[0]//2-loading.get_size()[0]//2, self.screen.get_size()[1]//2-loading.get_size()[1]//2])
        pygame.event.get()
        pygame.display.flip()
        self.paused = True
        self.save_file = os.getcwd()+os.sep+"save.json"

        self.points = 0
        self.player_pos = Vector(2, 2)
        self.moved_from = self.player_pos.copy()
        coin_x = utils.random_exclude(0, 4, self.player_pos.x)
        coin_y = utils.random_exclude(0, 4, self.player_pos.y)
        self.coin_pos = Vector(coin_x, coin_y)
        self.bg_px_s = 20
        self.bg_surf = self.remake_bg()
        gridmeta = {
            "s_x": 100,
            "s_y": 100,
            "sp_x": 50,
            "sp_y": 50,
            "rows": 5,
            "cols": 5
        }
        self.gridmeta = gridmeta
        self.field = self.create_grid(gridmeta["s_x"], gridmeta["s_y"], gridmeta["sp_x"], gridmeta["sp_y"], gridmeta["rows"], gridmeta["cols"])
        self.player_sprites =  assetsutils.get_looped_r("player")
        self.coin_sprites = assetsutils.get_looped_r("coin")
        self.clock_sprites = assetsutils.get_looped("clock", os.sep+"clock")
        self.muted_sprites = assetsutils.get_looped("muted")
        self.reset_icon = assetsutils.get_image(assetsutils.assets_folder+os.sep+"reset.png")
        self.restart_icon = assetsutils.get_image(assetsutils.assets_folder+os.sep+"restart.png")
        self.coin_sound = pygame.mixer.Sound(assetsutils.assets_folder+os.sep+"coin.mp3")
        self.move_sound = pygame.mixer.Sound(assetsutils.assets_folder+os.sep+"move.wav")
        self.mute = False
        self.player = 0
        self.coin_anim = 0
        self.clock_anim = 0
        self.grid = self.get_field()
        self.repos_grid()
        self.start_time = datetime.utcnow().timestamp()
        self.delta = 0
        self.pause_time = datetime.utcnow().timestamp()
        self.pause_delta = 0.0
        self.best = -1
        self.time_results = []
        self.avg_time = 0.0
        self.last_add = 0
        self.reset_time = 0
        self.time_to_reset = 120
        self.x_hold = False
        self.restarted = False
        try:
            self.load_data()
        except Exception as e:
            print("Failed to load:", e)

    def start(self):
        self.running = True
        self.game_loop()

    def stop(self):
        self.running = False
        self.save_data()

    def at_exit(self):
        print(f"Quitting after {self.tick} ticks")
        pygame.quit()
    
    def save_data(self):
        d = {
            "mute": self.mute,
            "avg_time": self.avg_time,
            "points": self.points,
            "best": self.best,
            "results": self.time_results
        }
        j = json.dumps(d, indent=4)
        try:
            with open(self.save_file, "w", encoding="utf8") as f:
                f.write(j)
        except Exception as e:
            print("Failed to save:", e)
    
    def load_data(self):
        if not os.path.exists(self.save_file):
            return
        with open(self.save_file, encoding="utf8") as f:
            s = f.read()
            d = json.loads(s)
            self.time_results: list[float] = d["results"]
            self.avg_time: float = d["avg_time"]
            self.points: int = d["points"]
            self.best: float = d["best"]
            self.mute: bool = d["mute"]
    
    def on_pause(self, resume):
        if resume:
            self.start_time = self.start_time+self.pause_delta
            self.restarted = False
            return
        self.pause_delta = 0.0
        self.pause_time = datetime.utcnow().timestamp()
        self.save_data()
    
    def do_reset(self):
        self.restart()
        self.points = 0
        self.avg_time = 0.0
        self.best = -1
        self.save_data()
        self.time_results = []
    
    def restart(self):
        self.restarted = True
        self.player_pos = Vector(2, 2)
        self.moved_from = self.player_pos.copy()
        coin_x = utils.random_exclude(0, 4, self.player_pos.x)
        coin_y = utils.random_exclude(0, 4, self.player_pos.y)
        self.coin_pos = Vector(coin_x, coin_y)
        self.last_add = 0
        self.delta = 0
        self.start_time = self.start_time+self.pause_delta
        self.pause_time = self.pause_time = datetime.utcnow().timestamp()
        if not self.mute:
                pygame.mixer.Sound.play(self.coin_sound)
    
    def update(self):
        if not self.x_hold:
            if self.reset_time > 0:
                    self.reset_time -= 1
        if self.paused:
            self.pause_delta = datetime.utcnow().timestamp()-self.pause_time
            if self.x_hold == True and self.reset_time < self.time_to_reset:
                self.reset_time += 1 
            if self.reset_time == self.time_to_reset:
                self.reset_time = 0
                self.do_reset()
            return
        self.loopvec(self.player_pos)
        self.loopvec(self.moved_from)
        
        if not utils.eq_vec(self.player_pos, self.moved_from):
            self.on_move(self.moved_from, self.player_pos)
            self.moved_from = self.player_pos.copy()
        
        if self.tick % 50 == 0:
            self.player = self.player+1
        if self.player == len(self.player_sprites):
            self.player = 0
        
        if self.tick % 20 == 0:
            self.coin_anim = self.coin_anim+1
        if self.coin_anim == len(self.coin_sprites):
            self.coin_anim = 0
        
        if self.tick % 3 == 0:
            self.clock_anim = self.clock_anim+1
        if self.clock_anim == len(self.clock_sprites):
            self.clock_anim = 0

        self.delta = (datetime.utcnow().timestamp()-self.start_time)
        if utils.eq_vec(self.coin_pos, self.player_pos):
            new_x = utils.random_exclude(0, 4, self.player_pos.x)
            new_y = utils.random_exclude(0, 4, self.player_pos.y)
            self.coin_pos = Vector(new_x, new_y)
            self.start_time = datetime.utcnow().timestamp()
            self.time_results.append(self.delta)
            if self.best == -1:
                self.best = min(self.time_results)
            else:
                self.best = min(self.time_results+[self.best])
            d = len(self.time_results) - 100
            if d > 0:
                for _ in range(d):
                    self.time_results.pop(0)
            self.avg_time = sum(self.time_results) / len(self.time_results)
            self.last_add = int(100*(1.120/self.delta))+100
            self.points += self.last_add
            if not self.mute:
                pygame.mixer.Sound.play(self.coin_sound)
    
    def draw_debug_rect(self, surf: pygame.Surface | pygame.Rect):
        isrect = False
        try:
            surf.get_rect()
        except:
            isrect = True
        if isrect:
            pygame.draw.rect(self.screen, utils.random_col(), surf, 1)
        else:
            pygame.draw.rect(self.screen, utils.random_col(), surf.get_rect(), 1)
    
    def draw_right(self):
        time_s = "{:.3f}".format(self.delta)
        deltaText = textutils.render_w_shadow(time_s, int(20*self.size_ratio[1]), self.main_font, (255, 255, 0), file=True)
        clock: pygame.Surface = self.clock_sprites[self.clock_anim]
        delta_clock_y_dif = abs(deltaText.get_size()[1]-clock.get_size()[1])
        clockpos = [self.screen.get_size()[0]-clock.get_size()[0]-int(10*self.size_ratio[0]), int(10*self.size_ratio[1])-delta_clock_y_dif//2]
        self.screen.blit(clock, clockpos)
        self.screen.blit(deltaText, [clockpos[0]-deltaText.get_size()[0]-10, deltaText.get_size()[1]-int(10*self.size_ratio[1])])

        avgText = textutils.render_w_shadow("avg: {:.3f}".format(self.avg_time), int(20*self.size_ratio[1]), self.main_font, (255, 255, 0), file=True)
        self.screen.blit(avgText, [self.screen.get_size()[0]-avgText.get_size()[0]-int(10*self.size_ratio[0]), deltaText.get_size()[1]+10+avgText.get_size()[1]-int(10*self.size_ratio[1])])
    
    def draw_left(self):
        if self.best != -1:
            best = "{:.3f}".format(self.best)
        else:
            best = "-"
        bestText = textutils.render_w_shadow("Best: "+best, int(20*self.size_ratio[1]), self.main_font, (230, 48, 127), file=True)
        # tickText = textutils.render_w_shadow("Tick #"+str(self.tick), int(20*self.size_ratio[1]), self.main_font, (255, 255, 0), file=True)
        # self.screen.blit(tickText, [int(10*self.size_ratio[0]), int(10*self.size_ratio[1])])
        self.screen.blit(bestText, [int(10*self.size_ratio[0]), int(10*self.size_ratio[1])])
        mark = textutils.render_w_shadow("github.com/BoBkiNN", int(10*self.size_ratio[1]), self.main_font, (230, 48, 127), file=True)
        self.screen.blit(mark, [int(5*self.size_ratio[0]), self.screen.get_size()[1]-int(10*self.size_ratio[1])-mark.get_size()[1]])
    
    def draw_paused(self):
        layer = pygame.Surface(self.window_size, pygame.SRCALPHA)
        layer.fill((0, 0, 0, 90))
        # paused_s = "{:.3f}".format(self.pause_delta)
        pausedText = textutils.render_w_shadow("PAUSE", int(40*self.size_ratio[1]), self.main_font, (255, 255, 255), file=True)
        time = textutils.render_w_shadow("Press any key to resume", int(20*self.size_ratio[1]), self.main_font, (255, 255, 255), file=True)
        layer.blit(pausedText, [layer.get_size()[0]//2-pausedText.get_size()[0]//2, layer.get_size()[1]//3])
        r2 = layer.blit(time, [layer.get_size()[0]//2-time.get_size()[0]//2, layer.get_size()[1]//3+pausedText.get_size()[1]+10])

        mute_text = textutils.render_w_shadow("Press M to (un)mute", int(20*self.size_ratio[1]), self.main_font, (255, 255, 255), file=True)
        row2_size = [60+10+mute_text.get_size()[0], max(60, mute_text.get_size()[1])]
        mute_pos = [layer.get_size()[0]//2-row2_size[0]//2, r2.bottomright[1]+int(20*self.size_ratio[1])]
        r3 = layer.blit(self.muted_sprites[int(not self.mute)], mute_pos)
        r4 = layer.blit(mute_text, [layer.get_size()[0]//2-row2_size[0]//2+60+20, r2.bottomright[1]+int(20*self.size_ratio[1])+30-mute_text.get_size()[1]//2])
        r5 = r3.union(r4)

        row2 = utils.UiRow(pygame.Surface(self.window_size, pygame.SRCALPHA))
        restart_text = textutils.render_w_shadow("Press R to restart", int(20*self.size_ratio[1]), self.main_font, (255, 255, 255), file=True)
        row2.add(self.restart_icon)
        row2.add(restart_text, offset=10)
        row2r = row2.render()
        r5 = layer.blit(row2r, [layer.get_size()[0]//2-row2r.get_size()[0]//2, r5.bottom+int(10*self.size_ratio[1])])

        row3 = utils.UiRow(pygame.Surface(self.window_size, pygame.SRCALPHA))
        reset_text = textutils.render_w_shadow("Hold X to reset", int(20*self.size_ratio[1]), self.main_font, (235, 52, 110), file=True)
        row3.add(self.reset_icon)
        row3.add(reset_text, offset=10)
        b3 = row3.render()
        b3r = b3.get_rect()
        # r6 = layer2.blit(hold_x_text, [layer2.get_size()[0]//2-hold_x_text.get_size()[0]//2 , r5.bottom+int(20*self.size_ratio[1])])
        reset_row = pygame.Surface([b3r.size[0], b3r.size[1]+int(7*self.size_ratio[1])+20], pygame.SRCALPHA)
        reset_row.blit(b3, [0, 0])

        hold_noise_x = 0
        hold_noise_y = 0
        
        if self.x_hold == True or self.reset_time != 0:
            # print(self.reset_time)
            p = self.reset_time/self.time_to_reset
            if p < 0:
                p = 0
            lenght = b3r.size[0]
            delta = lenght*p
            hold_noise_x = random.randint(-20, 20)*p
            hold_noise_y = random.randint(-20, 20)*p
            pygame.draw.line(reset_row, (235, 52, 110), [b3r.x, b3r.y+int(7*self.size_ratio[1])+b3r.size[1]], [b3r.left+delta, b3r.y+int(7*self.size_ratio[1])+b3r.size[1]], 10)
        layer.blit(reset_row, [layer.get_size()[0]//2-reset_row.get_size()[0]//2+hold_noise_x, r5.bottom+int(10*self.size_ratio[1])+hold_noise_y])
        self.screen.blit(layer, [0, 0])

    def render(self):
        self.screen.fill((0, 0, 0))
        self.screen.blit(self.bg_surf, [0, 0])
        self.screen.blit(self.grid, self.gridpos)
        # pygame.draw.rect(self.screen, (255, 255, 0), grid_rect, 2)
        cell: dict = self.field[self.player_pos.y][self.player_pos.x]
        cell_r: pygame.Rect = cell["r"]
        player: pygame.Surface = self.player_sprites[self.player]
        player_size = player.get_size()
        px = cell["x"]+(cell_r.size[0]//2 - player_size[0]//2)+self.gridpos[0]
        py = cell["y"]+(cell_r.size[1]//2 - player_size[1]//2)+self.gridpos[1]
        # pygame.draw.rect(self.screen, (255, 255, 255), pygame.Rect(px, py, self.player_size[0], self.player_size[1]))
        self.screen.blit(player, [px, py])

        cell_c: dict = self.field[self.coin_pos.y][self.coin_pos.x]
        cell_c_r: pygame.Rect = cell_c["r"]
        coin = self.coin_sprites[self.coin_anim]
        cx = cell_c["x"]+(cell_c_r.size[0]//2 - coin.get_size()[0]//2)+self.gridpos[0]
        cy = cell_c["y"]+(cell_c_r.size[1]//2 - coin.get_size()[1]//2)+self.gridpos[1]

        self.screen.blit(coin, [cx, cy])

        addText = ""
        if self.last_add != 0:
            addText = " +"+str(self.last_add)
        pointsText = textutils.render_w_shadow(str(self.points)+addText, int(20*self.size_ratio[1]), self.main_font, (51, 255, 177), file=True)
        self.screen.blit(pointsText, [self.screen.get_rect().centerx-pointsText.get_size()[0]//2, pointsText.get_size()[1]])

        self.draw_right()
        self.draw_left()
        if self.paused:
            self.draw_paused()
        pygame.display.flip()
    
    def repos_grid(self):
        gridsize = self.grid.get_size()
        gr_x = self.window_size[0]//2-gridsize[0]//2
        gr_y = self.window_size[1]//2-gridsize[1]//2
        self.gridpos = [gr_x, gr_y]
    
    def on_resize(self, w, h):
        self.window_size = (w, h)
        self.size_ratio = (w/self.original_size[0], h/self.original_size[1])
        if self.fullscreen:
            self.screen = pygame.display.set_mode(self.window_size, pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode(self.window_size, pygame.RESIZABLE)
        self.bg_surf = self.remake_bg()
        gridmeta = self.gridmeta
        self.field = self.create_grid(gridmeta["s_x"], gridmeta["s_y"], gridmeta["sp_x"], gridmeta["sp_y"], gridmeta["rows"], gridmeta["cols"])
        self.grid = self.get_field()
        self.repos_grid()
    
    def on_move(self, fr: Vector, to: Vector):
        # print("Moved ", fr, "->", to)
        cell_f: dict = self.field[fr.y][fr.x]
        cell_t: dict = self.field[to.y][to.x]
        if not self.mute:
            pygame.mixer.Sound.play(self.move_sound)
    
    def on_key_press(self, key, up: bool):
        if up: 
            if key == pygame.K_x:
                self.x_hold = False
            return
        not_any = [1073742051, pygame.K_PRINTSCREEN, pygame.K_m, pygame.K_x, pygame.K_r, pygame.K_F11]
        if self.paused and key not in not_any:
            self.paused = not self.paused
            self.on_pause(not self.paused)
        elif key == pygame.K_SPACE or key == pygame.K_ESCAPE:
            self.paused = not self.paused
            self.on_pause(not self.paused)
        if key == pygame.K_m:
            self.mute = not self.mute
        if key == pygame.K_r:
            self.restart()
        if key == pygame.K_F11:
            self.fullscreen = not self.fullscreen
            if self.fullscreen:
                self.on_resize(self.m_info.current_w, self.m_info.current_h)
            else:
                self.on_resize(self.original_size[0], self.original_size[1])
        if self.paused:
            if key == pygame.K_x:
                self.x_hold = True
            return
        self.reset_time = 0
        if key == pygame.K_UP:
            self.moved_from = self.player_pos.copy()
            self.player_pos.add(0, -1)
        elif key == pygame.K_DOWN:
            self.moved_from = self.player_pos.copy()
            self.player_pos.add(0, 1)
        elif key == pygame.K_LEFT:
            self.moved_from = self.player_pos.copy()
            self.player_pos.add(-1, 0)
        elif key == pygame.K_RIGHT:
            self.moved_from = self.player_pos.copy()
            self.player_pos.add(1, 0)

    def process_events(self):
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                self.stop()
            if e.type == pygame.VIDEORESIZE:
                self.on_resize(e.w, e.h)
            if e.type == pygame.KEYDOWN:
                self.on_key_press(e.key, False)
            if e.type == pygame.KEYUP:
                self.on_key_press(e.key, True)
    
    def game_loop(self):
        while self.running:
            self.tick+=1
            self.process_events()
            self.update()
            self.render()
            self.post_tick()
    
    def post_tick(self):
        self.clock.tick(60)

def main():
    Game().start()

if __name__ == "__main__":
    main()
