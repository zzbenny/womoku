# -*- coding: utf-8 -*-
import pygame
import sys
import numpy as np
from ai import GomokuAI
import time

# 初始化 Pygame
pygame.init()

# 常量定义
BOARD_SIZE = 15
CELL_SIZE = 40
MARGIN = 40
PIECE_RADIUS = 18
WINDOW_SIZE = BOARD_SIZE * CELL_SIZE + 2 * MARGIN

# 颜色定义
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BROWN = (205, 133, 63)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

class GomokuGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
        pygame.display.set_caption('五子棋')
        self.board = np.zeros((BOARD_SIZE, BOARD_SIZE), dtype=int)
        self.current_player = 1  # 1: 黑子, -1: 白子
        self.game_over = False
        self.winner = None
        self.ai = None
        self.difficulty = 'medium'
        # 使用系统默认字体
        try:
            self.font = pygame.font.SysFont('SimHei', 24)  # 使用黑体
        except:
            try:
                self.font = pygame.font.SysFont('Microsoft YaHei', 24)  # 尝试使用微软雅黑
            except:
                self.font = pygame.font.Font(None, 36)  # 使用默认字体
        self.last_move_time = 0
        self.move_delay = 0.1  # 移动延迟（秒）
        self.ai_thinking = False  # 添加AI思考状态标志
        
    def draw_board(self):
        # 绘制棋盘背景
        self.screen.fill(BROWN)
        
        # 绘制网格线
        for i in range(BOARD_SIZE):
            # 横线
            pygame.draw.line(self.screen, BLACK,
                           (MARGIN, MARGIN + i * CELL_SIZE),
                           (WINDOW_SIZE - MARGIN, MARGIN + i * CELL_SIZE))
            # 竖线
            pygame.draw.line(self.screen, BLACK,
                           (MARGIN + i * CELL_SIZE, MARGIN),
                           (MARGIN + i * CELL_SIZE, WINDOW_SIZE - MARGIN))
        
        # 绘制棋子
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                if self.board[i][j] != 0:
                    color = BLACK if self.board[i][j] == 1 else WHITE
                    center = (MARGIN + j * CELL_SIZE, MARGIN + i * CELL_SIZE)
                    # 绘制棋子阴影
                    pygame.draw.circle(self.screen, (128, 128, 128), 
                                    (center[0]+2, center[1]+2), PIECE_RADIUS)
                    # 绘制棋子
                    pygame.draw.circle(self.screen, color, center, PIECE_RADIUS)
                    # 如果是白子，添加边框
                    if color == WHITE:
                        pygame.draw.circle(self.screen, BLACK, center, PIECE_RADIUS, 1)
        
        # 绘制当前玩家和难度信息
        player_text = "当前玩家: 黑子" if self.current_player == 1 else "当前玩家: 白子"
        difficulty_text = f"AI难度: {self.difficulty}"
        help_text = "右键切换难度 | R键重置 | ESC退出"
        
        player_surface = self.font.render(player_text, True, BLACK)
        difficulty_surface = self.font.render(difficulty_text, True, BLACK)
        help_surface = self.font.render(help_text, True, BLACK)
        
        self.screen.blit(player_surface, (10, 10))
        self.screen.blit(difficulty_surface, (10, 40))
        self.screen.blit(help_surface, (10, WINDOW_SIZE - 30))
        
        if self.game_over:
            winner_text = "黑子获胜!" if self.winner == 1 else "白子获胜!"
            text_surface = self.font.render(winner_text, True, RED)
            text_rect = text_surface.get_rect(center=(WINDOW_SIZE//2, 30))
            self.screen.blit(text_surface, text_rect)
        
        pygame.display.flip()
    
    def get_board_position(self, mouse_pos):
        x, y = mouse_pos
        # 计算最近的棋盘交叉点
        row = round((y - MARGIN) / CELL_SIZE)
        col = round((x - MARGIN) / CELL_SIZE)
        if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE:
            return row, col
        return None
    
    def make_move(self, row, col):
        if self.board[row][col] == 0 and not self.game_over:
            self.board[row][col] = self.current_player
            if self.check_winner(row, col):
                self.game_over = True
                self.winner = self.current_player
            else:
                self.current_player = -self.current_player
            return True
        return False
    
    def check_winner(self, row, col):
        directions = [(1,0), (0,1), (1,1), (1,-1)]
        for dr, dc in directions:
            count = 1
            # 正向检查
            r, c = row + dr, col + dc
            while 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and self.board[r][c] == self.current_player:
                count += 1
                r += dr
                c += dc
            # 反向检查
            r, c = row - dr, col - dc
            while 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and self.board[r][c] == self.current_player:
                count += 1
                r -= dr
                c -= dc
            if count >= 5:
                return True
        return False
    
    def ai_move(self):
        if not self.game_over and self.current_player == -1 and not self.ai_thinking:
            current_time = time.time()
            if current_time - self.last_move_time >= self.move_delay:
                self.ai_thinking = True
                move = self.ai.get_move(self.board, self.current_player)
                if move:
                    self.make_move(move[0], move[1])
                    self.last_move_time = current_time
                self.ai_thinking = False
    
    def change_difficulty(self):
        difficulties = ['easy', 'medium', 'hard']
        current_index = difficulties.index(self.difficulty)
        self.difficulty = difficulties[(current_index + 1) % len(difficulties)]
        self.ai = GomokuAI(self.difficulty)
    
    def reset_game(self):
        self.board = np.zeros((BOARD_SIZE, BOARD_SIZE), dtype=int)
        self.current_player = 1
        self.game_over = False
        self.winner = None
        self.last_move_time = 0
        self.ai_thinking = False
        # 重置 AI
        self.ai = GomokuAI(self.difficulty)
        # 重置移动计数
        if self.ai:
            self.ai.move_count = 0

def main():
    game = GomokuGame()
    game.ai = GomokuAI(game.difficulty)
    clock = pygame.time.Clock()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and not game.ai_thinking:
                if event.button == 1:  # 左键点击
                    pos = game.get_board_position(event.pos)
                    if pos and not game.game_over and game.current_player == 1:
                        if game.make_move(pos[0], pos[1]):
                            game.draw_board()
                            pygame.time.wait(100)  # 等待一小段时间
                elif event.button == 3:  # 右键点击
                    game.change_difficulty()
                    game.reset_game()  # 切换难度时也重置游戏
            elif event.type == pygame.KEYUP:  # 改为 KEYUP 事件
                if event.key == pygame.K_r:  # 按R键重置游戏
                    print("重置游戏")  # 添加调试信息
                    game.reset_game()
                    game.draw_board()
                elif event.key == pygame.K_ESCAPE:  # 按ESC键退出
                    print("退出游戏")  # 添加调试信息
                    running = False
        
        # AI移动
        if game.current_player == -1 and not game.game_over and not game.ai_thinking:
            game.ai_move()
        
        game.draw_board()
        clock.tick(60)  # 限制帧率为60FPS
    
    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main() 