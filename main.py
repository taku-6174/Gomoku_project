import pygame
import numpy as np 
import sys

class GomokuAnalyzer:
    def __init__(self,size=15):
        self.size=size
        #0:空　1:黒（先手）　3:白（後手）　
        self.board=np.zeros((size,size),dtype=int)

    def put_stone(self,r,c,player):
        """石を置く。おければtrue,おけなければfalse"""
        if self.board[r][c]==0:
            self.board[r][c]=player
            return True
        return False

    def evaluate_board(self):
        scores = np.zeros((self.size, self.size))
        # チェックする方向（勝利判定と同じ）
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]

        for r in range(self.size):
            for c in range(self.size):
                if self.board[r][c] == 0:
                    # 基本スコア（真ん中に近いほど少し高い）
                    base_score = 10 - (abs(r - self.size//2) + abs(c - self.size//2))
                    total_score = max(0, base_score)

                    # --- 【ここから追加】石の並びをチェック ---
                    for dr, dc in directions:
                        # そのマスに置いたと仮定して、何個並ぶか数える
                        count = 1
                        # 正の方向
                        for i in range(1, 5):
                            nr, nc = r + dr * i, c + dc * i
                            if 0 <= nr < self.size and 0 <= nc < self.size and self.board[nr][nc] == 1: # プレイヤー1（黒）
                                count += 1
                            else: break
                        # 負の方向
                        for i in range(1, 5):
                            nr, nc = r - dr * i, c - dc * i
                            if 0 <= nr < self.size and 0 <= nc < self.size and self.board[nr][nc] == 1:
                                count += 1
                            else: break
                        
                        # 並び数に応じた加点（ここがAIの性格になる）
                        if count >= 5: total_score += 10000
                        elif count == 4: total_score += 1000
                        elif count == 3: total_score += 100
                    
                    scores[r][c] = total_score
                    max_val = np.max(scores)
                    if max_val > 0:
                        # すべてのスコアを最大値で割って、10を掛ける
                        # これで 0 〜 10 の間に収まる
                        scores = (scores / max_val) * 10
        return scores
                    

    def check_win(self,r,c,player):
        #(横、縦、左斜め、右斜め)
        directions=[(0,1),(1,0),(1,1),(1,-1)]

        for dr,dc in directions:
            count=1 #置いた碁を1つ目とする
            #指定された方向（正の向き）に連続する碁を数える
            for i in range(1,5):
                nr,nc=r+dr*i,c+dc*i
                if 0<=nr<self.size and 0<=nc<=self.size and self.board[nr][nc]==player:
                    count+=1
                else:
                     break

            #反対の方向も数える
            for i in range(1,5):
                nr,nc=r-dr*i,c-dc*i
                if 0<=nr<self.size and 0<=nc<=self.size and self.board[nr][nc]==player:
                    count+=1
                else:
                    break

            #５つ以上ならば勝利
            if count>=5:
                return True
        return False

#画面表示の設定
pygame.init()
CELL_SIZE=40
MARGIN=40
BOARD_SIZE=15
SCREEN_SIZE=CELL_SIZE*(BOARD_SIZE-1)+MARGIN*2
screen=pygame.display.set_mode((SCREEN_SIZE,SCREEN_SIZE))
pygame.display.set_caption("五目並べ　解析シミュレーター")
font=pygame.font.SysFont("arial",12)

def draw_board(analyzer):
    #背景色
    screen.fill((220,179,92))

    #線の描画
    for i in range(BOARD_SIZE):
        pygame.draw.line(screen,(0,0,0),(MARGIN,MARGIN+i*CELL_SIZE),(SCREEN_SIZE-MARGIN,MARGIN+i*CELL_SIZE),2)
        pygame.draw.line(screen,(0,0,0),(MARGIN+i*CELL_SIZE,MARGIN),(MARGIN+i*CELL_SIZE,SCREEN_SIZE-MARGIN),2)

    #石と「AIのヒント」の描画
    scores=analyzer.evaluate_board()
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            #石の描画
            if analyzer.board[r][c]==1:
                pygame.draw.circle(screen,(0,0,0),(MARGIN+c*CELL_SIZE,MARGIN+r*CELL_SIZE),18)
            elif analyzer.board[r][c]==2:
                pygame.draw.circle(screen,(225,255,255),(MARGIN+c*CELL_SIZE,MARGIN+r*CELL_SIZE),18)
            #空きますにAIのスコアを表示
            elif scores[r][c]>0:
                score_text=font.render(str(int(scores[r][c])),True,(100,100,100))
                screen.blit(score_text,(MARGIN+c*CELL_SIZE-5,MARGIN+r*CELL_SIZE-5))

#メインループ
analyzer=GomokuAnalyzer()
current_player=1

while True:
    draw_board(analyzer)
    pygame.display.flip()

    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type==pygame.MOUSEBUTTONDOWN:
            mx,my=pygame.mouse.get_pos()
            #クリック位置を盤面の行列(r,c)に変換
            c=round((mx-MARGIN)/CELL_SIZE)
            r=round((my-MARGIN)/CELL_SIZE)

            if analyzer.put_stone(r,c,current_player):
                if analyzer.check_win(r,c,current_player):
                    print(f"プレイヤー{current_player}の勝利！")

                current_player=2 if current_player==1 else 1