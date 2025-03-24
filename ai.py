import numpy as np
from typing import Tuple, List
import time

class GomokuAI:
    def __init__(self, difficulty: str = 'medium'):
        self.difficulty = difficulty
        self.depths = {
            'easy': 4,    # 增加基础深度
            'medium': 5,
            'hard': 6
        }
        self.depth = self.depths.get(difficulty, 5)
        # 开局库
        self.opening_moves = [
            [(7,7)],  # 天元
            [(7,7), (7,8)],  # 天元+右
            [(7,7), (8,8)],  # 天元+右下
            [(7,7), (6,8)],  # 天元+右上
            [(7,7), (8,7)],  # 天元+下
            [(7,7), (6,7)],  # 天元+上
            [(7,7), (7,6)],  # 天元+左
        ]
        self.move_count = 0
        # 缓存最近的计算结果
        self.cache = {}
        self.cache_size = 10000
        
    def get_move(self, board: np.ndarray, player: int) -> Tuple[int, int]:
        """获取 AI 的下一步移动"""
        # 检查是否在开局阶段
        if self.move_count < 4:
            for opening in self.opening_moves:
                if self.move_count < len(opening):
                    move = opening[self.move_count]
                    if board[move[0]][move[1]] == 0:
                        self.move_count += 1
                        return move
        
        # 检查缓存
        board_key = self._board_to_key(board)
        if board_key in self.cache:
            return self.cache[board_key]
        
        best_score = float('-inf')
        best_move = None
        alpha = float('-inf')
        beta = float('inf')
        
        # 获取所有可能的移动，并按照威胁度排序
        possible_moves = self._get_possible_moves(board)
        possible_moves = self._sort_moves_by_threat(board, possible_moves, player)
        
        # 增加搜索的移动数量
        possible_moves = possible_moves[:20]  # 从15增加到20
        
        for move in possible_moves:
            board[move[0]][move[1]] = player
            score = self._minimax(board, self.depth - 1, False, alpha, beta, -player)
            board[move[0]][move[1]] = 0
            
            if score > best_score:
                best_score = score
                best_move = move
            alpha = max(alpha, best_score)
        
        # 保存到缓存
        if len(self.cache) < self.cache_size:
            self.cache[board_key] = best_move
        
        self.move_count += 1
        return best_move
    
    def _board_to_key(self, board: np.ndarray) -> str:
        """将棋盘状态转换为缓存键"""
        return str(board.tobytes())
    
    def _minimax(self, board: np.ndarray, depth: int, is_maximizing: bool, 
                 alpha: float, beta: float, player: int) -> float:
        """极大极小算法实现"""
        if depth == 0 or self._is_game_over(board):
            return self._evaluate_board(board, player)
            
        if is_maximizing:
            max_eval = float('-inf')
            for move in self._get_possible_moves(board)[:10]:  # 从8增加到10
                board[move[0]][move[1]] = player
                eval = self._minimax(board, depth - 1, False, alpha, beta, -player)
                board[move[0]][move[1]] = 0
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float('inf')
            for move in self._get_possible_moves(board)[:10]:  # 从8增加到10
                board[move[0]][move[1]] = player
                eval = self._minimax(board, depth - 1, True, alpha, beta, -player)
                board[move[0]][move[1]] = 0
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval
    
    def _get_possible_moves(self, board: np.ndarray) -> List[Tuple[int, int]]:
        """获取所有可能的移动"""
        moves = []
        # 只考虑已有棋子周围的空位
        for i in range(len(board)):
            for j in range(len(board[0])):
                if board[i][j] == 0 and self._has_neighbor(board, i, j):
                    moves.append((i, j))
        return moves if moves else [(len(board)//2, len(board[0])//2)]
    
    def _has_neighbor(self, board: np.ndarray, row: int, col: int) -> bool:
        """检查是否有相邻的棋子"""
        for i in range(max(0, row-2), min(len(board), row+3)):
            for j in range(max(0, col-2), min(len(board[0]), col+3)):
                if board[i][j] != 0:
                    return True
        return False
    
    def _sort_moves_by_threat(self, board: np.ndarray, moves: List[Tuple[int, int]], player: int) -> List[Tuple[int, int]]:
        """根据威胁度对移动进行排序"""
        move_scores = []
        for move in moves:
            score = 0
            # 检查是否能形成五连
            board[move[0]][move[1]] = player
            if self._is_game_over(board):
                score += 1000000
            # 检查是否能阻止对手五连
            board[move[0]][move[1]] = -player
            if self._is_game_over(board):
                score += 900000
            # 检查是否能形成活四
            board[move[0]][move[1]] = player
            if self._count_pattern(board, move[0], move[1], player, 4, True):
                score += 100000
            # 检查是否能阻止对手活四
            board[move[0]][move[1]] = -player
            if self._count_pattern(board, move[0], move[1], -player, 4, True):
                score += 90000
            # 检查是否能形成活三
            board[move[0]][move[1]] = player
            if self._count_pattern(board, move[0], move[1], player, 3, True):
                score += 10000
            # 检查是否能阻止对手活三
            board[move[0]][move[1]] = -player
            if self._count_pattern(board, move[0], move[1], -player, 3, True):
                score += 9000
            # 检查是否能形成活二
            board[move[0]][move[1]] = player
            if self._count_pattern(board, move[0], move[1], player, 2, True):
                score += 1000
            # 检查是否能阻止对手活二
            board[move[0]][move[1]] = -player
            if self._count_pattern(board, move[0], move[1], -player, 2, True):
                score += 900
            # 检查是否能形成跳三
            board[move[0]][move[1]] = player
            if self._count_jump_pattern(board, move[0], move[1], player, 3):
                score += 8000
            # 检查是否能阻止对手跳三
            board[move[0]][move[1]] = -player
            if self._count_jump_pattern(board, move[0], move[1], -player, 3):
                score += 7000
            # 检查是否能形成双活三
            board[move[0]][move[1]] = player
            if self._count_double_pattern(board, move[0], move[1], player, 3):
                score += 50000
            # 检查是否能阻止对手双活三
            board[move[0]][move[1]] = -player
            if self._count_double_pattern(board, move[0], move[1], -player, 3):
                score += 45000
            board[move[0]][move[1]] = 0
            move_scores.append((move, score))
        
        # 根据分数排序
        move_scores.sort(key=lambda x: x[1], reverse=True)
        return [move for move, _ in move_scores]
    
    def _count_pattern(self, board: np.ndarray, row: int, col: int, player: int, length: int, is_alive: bool) -> bool:
        """计算特定模式的连续棋子数"""
        directions = [(1,0), (0,1), (1,1), (1,-1)]
        for dr, dc in directions:
            count = 1
            # 正向检查
            r, c = row + dr, col + dc
            while 0 <= r < len(board) and 0 <= c < len(board[0]) and board[r][c] == player:
                count += 1
                r += dr
                c += dc
            # 反向检查
            r, c = row - dr, col - dc
            while 0 <= r < len(board) and 0 <= c < len(board[0]) and board[r][c] == player:
                count += 1
                r -= dr
                c -= dc
            if count >= length:
                if is_alive:
                    # 检查两端是否都是空位
                    r1, c1 = row + dr * count, col + dc * count
                    r2, c2 = row - dr * count, col - dc * count
                    if (0 <= r1 < len(board) and 0 <= c1 < len(board[0]) and board[r1][c1] == 0 and
                        0 <= r2 < len(board) and 0 <= c2 < len(board[0]) and board[r2][c2] == 0):
                        return True
                else:
                    return True
        return False
    
    def _count_jump_pattern(self, board: np.ndarray, row: int, col: int, player: int, length: int) -> bool:
        """计算跳连模式（如：X-X-X）"""
        directions = [(1,0), (0,1), (1,1), (1,-1)]
        for dr, dc in directions:
            count = 1
            # 正向检查
            r, c = row + dr, col + dc
            while 0 <= r < len(board) and 0 <= c < len(board[0]):
                if board[r][c] == player:
                    count += 1
                elif board[r][c] != 0:
                    break
                r += dr
                c += dc
            # 反向检查
            r, c = row - dr, col - dc
            while 0 <= r < len(board) and 0 <= c < len(board[0]):
                if board[r][c] == player:
                    count += 1
                elif board[r][c] != 0:
                    break
                r -= dr
                c -= dc
            if count >= length:
                return True
        return False
    
    def _count_double_pattern(self, board: np.ndarray, row: int, col: int, player: int, length: int) -> bool:
        """计算双活三、双活四等模式"""
        count = 0
        directions = [(1,0), (0,1), (1,1), (1,-1)]
        for dr, dc in directions:
            if self._count_pattern(board, row, col, player, length, True):
                count += 1
        return count >= 2
    
    def _is_game_over(self, board: np.ndarray) -> bool:
        """检查游戏是否结束"""
        return self._count_pattern(board, 0, 0, 1, 5, False) or self._count_pattern(board, 0, 0, -1, 5, False)
    
    def _evaluate_board(self, board: np.ndarray, player: int) -> float:
        """评估当前棋盘状态"""
        score = 0
        # 评估连续棋子
        for i in range(len(board)):
            for j in range(len(board[0])):
                if board[i][j] == player:
                    # 检查周围8个方向
                    for di in [-1, 0, 1]:
                        for dj in [-1, 0, 1]:
                            if di == 0 and dj == 0:
                                continue
                            count = 1
                            ni, nj = i + di, j + dj
                            while 0 <= ni < len(board) and 0 <= nj < len(board[0]) and board[ni][nj] == player:
                                count += 1
                                ni += di
                                nj += dj
                            # 增加连续棋子的评分
                            if count >= 5:
                                score += 100000
                            elif count == 4:
                                score += 10000
                            elif count == 3:
                                score += 1000
                            elif count == 2:
                                score += 100
                elif board[i][j] == -player:
                    # 对对手的棋子进行负分评估
                    for di in [-1, 0, 1]:
                        for dj in [-1, 0, 1]:
                            if di == 0 and dj == 0:
                                continue
                            count = 1
                            ni, nj = i + di, j + dj
                            while 0 <= ni < len(board) and 0 <= nj < len(board[0]) and board[ni][nj] == -player:
                                count += 1
                                ni += di
                                nj += dj
                            # 增加对手连续棋子的负分
                            if count >= 5:
                                score -= 90000
                            elif count == 4:
                                score -= 9000
                            elif count == 3:
                                score -= 900
                            elif count == 2:
                                score -= 90
        
        # 评估棋子的位置
        for i in range(len(board)):
            for j in range(len(board[0])):
                if board[i][j] == player:
                    # 中心位置加分
                    if 3 <= i <= 11 and 3 <= j <= 11:
                        score += 50
                    # 靠近中心的位置加分
                    elif 2 <= i <= 12 and 2 <= j <= 12:
                        score += 30
                elif board[i][j] == -player:
                    # 对手的中心位置减分
                    if 3 <= i <= 11 and 3 <= j <= 11:
                        score -= 45
                    # 对手靠近中心的位置减分
                    elif 2 <= i <= 12 and 2 <= j <= 12:
                        score -= 25
        
        return score 