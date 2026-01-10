import pygame
import numpy as np 
import sys
import os


class GomokuAnalyzer:
    def __init__(self, size=15):
        self.size = size
        self.board = np.zeros((size, size), dtype=int)
        self.current_player = 1  # 1:黒（先手） 2:白（後手）
        self.move_history = []  # 着手履歴を記録
    
    def put_stone(self, r, c, player):
        """石を置く。置ければTrue、置けなければFalse"""
        if 0 <= r < self.size and 0 <= c < self.size and self.board[r][c] == 0:
            self.board[r][c] = player
            self.move_history.append((r, c, player))  # 履歴に追加
            return True
        return False
    
    def evaluate_board(self, for_player=None):
        """指定したプレイヤー視点で盤面を評価"""
        if for_player is None:
            for_player = self.current_player
        
        scores = np.zeros((self.size, self.size))
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        
        for r in range(self.size):
            for c in range(self.size):
                if self.board[r][c] == 0:
                    # 基本スコア（中央に近いほど高い）
                    center = self.size // 2
                    distance = abs(r - center) + abs(c - center)
                    total_score = max(1, 20 - distance)
                    
                    # 攻撃評価
                    for player in [1, 2]:
                        player_score = 0
                        for dr, dc in directions:
                            count = 1
                            
                            # 正方向
                            for i in range(1, 5):
                                nr, nc = r + dr * i, c + dc * i
                                if 0 <= nr < self.size and 0 <= nc < self.size and self.board[nr][nc] == player:
                                    count += 1
                                else:
                                    break
                            
                            # 負方向
                            for i in range(1, 5):
                                nr, nc = r - dr * i, c - dc * i
                                if 0 <= nr < self.size and 0 <= nc < self.size and self.board[nr][nc] == player:
                                    count += 1
                                else:
                                    break
                            
                            # 連続数による加点
                            if count >= 5:
                                player_score += 10000  # 勝利確定
                            elif count == 4:
                                player_score += 1000   # 四のでき
                            elif count == 3:
                                player_score += 100    # 三のでき
                            elif count == 2:
                                player_score += 10     # 二のでき
                        
                        # 攻撃 vs 防御の重み付け
                        if player == for_player:
                            total_score += player_score * 1.0  # 攻撃
                        else:
                            total_score += player_score * 1.2  # 防御を重視
                    
                    scores[r][c] = total_score
        
        # 0-10に正規化
        max_val = np.max(scores)
        if max_val > 0:
            scores = (scores / max_val) * 10
            scores = np.round(scores)  # 整数に丸める
        
        return scores
    
    def check_win(self, r, c, player):
        """勝利判定"""
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        
        for dr, dc in directions:
            count = 1
            
            # 正方向
            for i in range(1, 5):
                nr, nc = r + dr * i, c + dc * i
                if 0 <= nr < self.size and 0 <= nc < self.size and self.board[nr][nc] == player:
                    count += 1
                else:
                    break
            
            # 負方向
            for i in range(1, 5):
                nr, nc = r - dr * i, c - dc * i
                if 0 <= nr < self.size and 0 <= nc < self.size and self.board[nr][nc] == player:
                    count += 1
                else:
                    break
            
            if count >= 5:
                return True
        
        return False
    
    def get_best_move(self):
        """最もスコアの高い手を返す"""
        scores = self.evaluate_board(self.current_player)
        
        max_score = -1
        best_moves = []
        
        for r in range(self.size):
            for c in range(self.size):
                if self.board[r][c] == 0:
                    score = scores[r][c]
                    if score > max_score:
                        max_score = score
                        best_moves = [(r, c, score)]
                    elif score == max_score:
                        best_moves.append((r, c, score))
        
        # 最高スコアの手からランダムに選択
        if best_moves:
            import random
            return random.choice(best_moves)[:2]  # (r, c)のみ返す
        return None
    
    def get_game_state(self):
        """ゲーム状態を文字列で返す"""
        state = []
        for r in range(self.size):
            row = []
            for c in range(self.size):
                if self.board[r][c] == 0:
                    row.append('.')
                elif self.board[r][c] == 1:
                    row.append('B')
                else:
                    row.append('W')
            state.append(''.join(row))
        return '\n'.join(state)

# Pygame設定
CELL_SIZE = 40
MARGIN = 50  # 情報表示用に余白を増やす
BOARD_SIZE = 15
SCREEN_WIDTH = CELL_SIZE * (BOARD_SIZE - 1) + MARGIN * 2
SCREEN_HEIGHT = SCREEN_WIDTH + 80  # 下部に情報表示エリア追加
INFO_AREA_HEIGHT = 80

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("五目並べ AI解析シミュレーター - 九州大学芸術工学部 編入プロジェクト")

# 日本語フォントの設定
def get_japanese_font(size):
    """利用可能な日本語フォントを探す"""
    font_paths = [
        # Windows
        "C:/Windows/Fonts/msgothic.ttc",  # MS ゴシック
        "C:/Windows/Fonts/meiryo.ttc",    # メイリオ
        "C:/Windows/Fonts/yugothic.ttf",  # 游ゴシック
        # macOS
        "/System/Library/Fonts/ヒラギノ角ゴシック W4.ttc",
        "/System/Library/Fonts/ヒラギノ丸ゴ ProN W4.ttc",
        # Linux
        "/usr/share/fonts/truetype/takao-gothic/TakaoGothic.ttf",
        # 汎用
        "arial",  # フォールバック
    ]
    
    for path in font_paths:
        try:
            if os.path.exists(path):
                return pygame.font.Font(path, size)
            elif 'arial' in path.lower():
                return pygame.font.SysFont(path, size)
        except:
            continue
    
    # どのフォントも見つからない場合
    return pygame.font.SysFont(None, size)

# フォントの初期化
font_small = get_japanese_font(14)
font_medium = get_japanese_font(18)
font_large = get_japanese_font(24)
font_title = get_japanese_font(28)

def draw_board(analyzer, game_over, winner):
    """盤面と情報を描画"""
    # 背景（グラデーション風）
    for y in range(SCREEN_HEIGHT):
        color_value = 220 - (y / SCREEN_HEIGHT * 20)
        pygame.draw.line(screen, (color_value, 179, 92), (0, y), (SCREEN_WIDTH, y))
    
    # 盤面背景（木目調）
    board_bg = pygame.Rect(
        MARGIN - 15, MARGIN - 15,
        CELL_SIZE * (BOARD_SIZE - 1) + 30,
        CELL_SIZE * (BOARD_SIZE - 1) + 30
    )
    pygame.draw.rect(screen, (199, 155, 95), board_bg)
    pygame.draw.rect(screen, (150, 110, 70), board_bg, 3)
    
    # 罫線
    for i in range(BOARD_SIZE):
        # 横線
        start_x, start_y = MARGIN, MARGIN + i * CELL_SIZE
        end_x, end_y = SCREEN_WIDTH - MARGIN, start_y
        pygame.draw.line(screen, (0, 0, 0), (start_x, start_y), (end_x, end_y), 2)
        
        # 縦線
        start_x, start_y = MARGIN + i * CELL_SIZE, MARGIN
        end_x, end_y = start_x, SCREEN_HEIGHT - INFO_AREA_HEIGHT - MARGIN
        pygame.draw.line(screen, (0, 0, 0), (start_x, start_y), (end_x, end_y), 2)
    
    # 星のマーク（天元など）
    stars = [(3, 3), (3, 11), (7, 7), (11, 3), (11, 11)]
    for sr, sc in stars:
        x = MARGIN + sc * CELL_SIZE
        y = MARGIN + sr * CELL_SIZE
        pygame.draw.circle(screen, (0, 0, 0), (x, y), 5)
    
    # スコア計算と表示
    scores = analyzer.evaluate_board()
    best_move = analyzer.get_best_move()
    
    # 石と評価値の描画
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            x = MARGIN + c * CELL_SIZE
            y = MARGIN + r * CELL_SIZE
            
            # 石の描画
            if analyzer.board[r][c] == 1:  # 黒石
                # 影効果
                pygame.draw.circle(screen, (30, 30, 30), (x+2, y+2), 16)
                # 本体
                pygame.draw.circle(screen, (20, 20, 20), (x, y), 16)
                pygame.draw.circle(screen, (100, 100, 100), (x, y), 16, 2)
                
            elif analyzer.board[r][c] == 2:  # 白石
                # 影効果
                pygame.draw.circle(screen, (230, 230, 230), (x+2, y+2), 16)
                # 本体
                pygame.draw.circle(screen, (250, 250, 250), (x, y), 16)
                pygame.draw.circle(screen, (200, 200, 200), (x, y), 16, 2)
            
            # 空マスの評価値表示
            elif scores[r][c] > 0:
                score_value = int(scores[r][c])
                
                # スコアに応じた色
                if score_value >= 9:
                    color = (255, 50, 50)    # 赤: 最善手
                elif score_value >= 7:
                    color = (255, 150, 50)   # 橙: 良い手
                elif score_value >= 5:
                    color = (255, 255, 50)   # 黄: 普通
                elif score_value >= 3:
                    color = (50, 200, 50)    # 緑: 悪い手
                else:
                    color = (150, 150, 150)  # 灰: 非常に悪い
                
                # 背景円
                pygame.draw.circle(screen, (255, 255, 255, 180), (x, y), 14)
                pygame.draw.circle(screen, color, (x, y), 14, 2)
                
                # 評価値テキスト
                score_text = font_small.render(str(score_value), True, color)
                text_rect = score_text.get_rect(center=(x, y))
                screen.blit(score_text, text_rect)
    
    # AIの最善手をハイライト
    if best_move and not game_over:
        br, bc = best_move
        if analyzer.board[br][bc] == 0:
            bx = MARGIN + bc * CELL_SIZE
            by = MARGIN + br * CELL_SIZE
            # 点滅する赤い枠
            pulse = (pygame.time.get_ticks() // 300) % 2
            if pulse:
                pygame.draw.circle(screen, (255, 0, 0), (bx, by), 20, 3)
    
    # 情報表示エリア（下部）
    info_rect = pygame.Rect(0, SCREEN_HEIGHT - INFO_AREA_HEIGHT, SCREEN_WIDTH, INFO_AREA_HEIGHT)
    pygame.draw.rect(screen, (240, 240, 240), info_rect)
    pygame.draw.line(screen, (180, 180, 180), (0, SCREEN_HEIGHT - INFO_AREA_HEIGHT), 
                    (SCREEN_WIDTH, SCREEN_HEIGHT - INFO_AREA_HEIGHT), 2)
    
    # ゲーム情報
    info_y = SCREEN_HEIGHT - INFO_AREA_HEIGHT + 10
    
    # タイトル
    title = font_title.render("五目並べ AI解析ツール", True, (0, 60, 120))
    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 5))
    
    # 現在の手番
    player_text = font_medium.render(f"現在の手番: {'黒' if analyzer.current_player == 1 else '白'}", 
                                   True, (0, 0, 0))
    screen.blit(player_text, (20, info_y))
    
    # 着手数
    move_count = len(analyzer.move_history)
    count_text = font_small.render(f"着手数: {move_count}", True, (0, 0, 0))
    screen.blit(count_text, (20, info_y + 25))
    
    # 操作説明（右側）
    controls = [
        "【操作方法】",
        "スペース: 再開",
        "ESC: 終了"
    ]
    
    for i, text in enumerate(controls):
        control_text = font_small.render(text, True, (80, 80, 80))
        screen.blit(control_text, (SCREEN_WIDTH - 200, info_y + i * 20))

    
    # ゲーム終了時の表示
    if game_over and winner:
        # 半透明オーバーレイ
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        # 勝利メッセージ
        winner_color = "黒" if winner == 1 else "白"
        win_text = font_large.render(f"🎉 {winner_color}の勝利！ 🎉", True, (255, 255, 0))
        text_rect = win_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30))
        screen.blit(win_text, text_rect)
        
        # リスタート指示
        restart_text = font_medium.render("スペースキーで新しいゲームを開始", True, (255, 255, 255))
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
        screen.blit(restart_text, restart_rect)
        
        # 総着手数
        total_moves = font_small.render(f"総着手数: {len(analyzer.move_history)}手", True, (200, 200, 200))
        total_rect = total_moves.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        screen.blit(total_moves, total_rect)

# メインループ
def main():
    analyzer = GomokuAnalyzer()
    game_over = False
    winner = None
    
    clock = pygame.time.Clock()
    
    print("=" * 50)
    print("五目並べ AI解析シミュレーター")
    print("九州大学芸術工学部 編入プロジェクト")
    print("=" * 50)
    print()
    print("【ゲーム説明】")
    print("・黒が先手、白が後手です")
    print("・マス上の数字はAIの評価値です（1-10、高いほど良い手）")
    print("・赤い枠はAIが推薦する最善手です")
    print()
    print("【操作方法】")
    print("・盤面クリック: 石を置く")
    print("・スペースキー: ゲーム再開")
    print("・ESCキー: 終了")
    print("=" * 50)
    
    while True:
        # イベント処理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                
                elif event.key == pygame.K_SPACE:
                    # ゲーム再開
                    if game_over:
                        analyzer = GomokuAnalyzer()
                        game_over = False
                        winner = None
                        print("\n" + "=" * 30)
                        print("新しいゲームを開始します")
                        print("=" * 30)
            
            if not game_over and event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                
                # 盤面内のクリック判定
                if (MARGIN <= mx <= SCREEN_WIDTH - MARGIN and 
                    MARGIN <= my <= SCREEN_HEIGHT - INFO_AREA_HEIGHT - MARGIN):
                    
                    c = round((mx - MARGIN) / CELL_SIZE)
                    r = round((my - MARGIN) / CELL_SIZE)
                    
                    if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
                        if analyzer.put_stone(r, c, analyzer.current_player):
                            print(f"{'黒' if analyzer.current_player == 1 else '白'}: ({r}, {c}) に着手")
                            
                            if analyzer.check_win(r, c, analyzer.current_player):
                                winner = analyzer.current_player
                                game_over = True
                                print(f" {'黒' if winner == 1 else '白'}の勝利！ ")
                                print(f"総着手数: {len(analyzer.move_history)}手")
                            else:
                                analyzer.current_player = 2 if analyzer.current_player == 1 else 1
        
        # 描画
        draw_board(analyzer, game_over, winner)
        pygame.display.flip()
        clock.tick(60)  # 60FPSに制限

if __name__ == "__main__":
    main()