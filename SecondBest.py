#
# SecondBest.py 2023/5/27
#
import pyxel
WIDTH, HEIGHT = 100, 142
P1, P2 = 0, 1  # 白,赤
OB_XYWH = ((38,17,14,12), (62,17,14,12), (82,34,16,14), (86,62,18,14), 
           (66,85,20,16), (34,85,20,16), (14,62,18,14), (18,34,16,14))  # ボード上の駒
IH_X, IH_Y, IH_W, IH_H = 50, 118, 20, 18  # 持ち駒
CMSG_X, CMSG_Y, CMSG_W, CMSG_H = 50, 49, 36, 32  # 中央メッセージ
LMSG_X, LMSG_Y, LMSG_W, LMSG_H = 4, 105, 31, 26  # 左メッセージ
RMSG_X, RMSG_Y, RMSG_W, RMSG_H = 65, 105, 31, 26  # 右メッセージ
COL = ((7,13,6), (8,2,14))  # 色：駒、影、光
ST_TITLE, ST_START, ST_COM, ST_MOTION, ST_TAKE, ST_PLACE, ST_JUDGE, ST_END = 0, 1, 2, 3, 4, 5, 6, 7  # 全体の状況
SB_DONE, SB_DISABLE, SB_ENABLE, SB_MUST = 100, 101, 102, 103  #　セカンドベストの状況
CUR_HAND, CUR_FINGER, CUR_HOLD, CUR_PLACE, CUR_CROSS = 200, 201, 202, 203, 204  # カーソル
VS_DEMO, VS_MAN, VS_COM = 300, 301, 302  # 対戦

class App:
    def start(self):
        self.turn = pyxel.rndi(P1, P2)
        self.win = [0, 0]  # 1勝ち
        self.ih = [0, 0]  # 持ち駒
        self.previh = []  # 一つ前の持ち駒　
        self.bd = [[] for _ in range(8)]  # ボード上の駒
        self.prevbd = []  # 一つ前のボード上の駒
        self.takepos = -1
        self.prevmove = [-1, -1]  # セカンドベスト後の同じ手は不可
        self.allmove, self.winidx, self.loseidx, self.drawidx, self.noneidx = [], [], [], [], []
        self.cnt = 0
        self.moveidx = -2  # コンピュータの手
        self.cursor_x, self.cursor_y = 0, 0
        self.mx, self.my = 0, 0  # マウスの位置
        self.cur = CUR_HAND  # カーソル
        self.sb = SB_DISABLE  #　セカンドベストの状況

    def init_piece(self):  # 駒初期化
        self.ih = [8,8]  # 持ち駒
        self.bd = [[] for _ in range(8)]  # ボード上の駒

    def __init__(self):
        pyxel.init(WIDTH, HEIGHT, title='Second Best')
        pyxel.load('assets/SecondBest.pyxres')
        pyxel.mouse(False)
        self.start()
        self.vs = VS_COM
        self.st = ST_TITLE
        pyxel.run(self.update, self.draw)

    def recboard(self):  # 盤面を保存
        self.previh = self.ih[:]
        self.prevbd = [pcs[:] for pcs in self.bd]

    def judge(self, board):  # 勝ち判定
        win = [0, 0]
        for pcs in board:
            if len(pcs)==3 and len(set(pcs))==1:  # ３重なり
                win[pcs[0]] = 1
        seq = [pcs[-1] if pcs else -1 for pcs in board]  # 一番上のみ取り出す
        seq.extend(seq[:3])  # 最初の３つを最後に追加
        for i in range(8):
            if seq[i] in (P1, P2) and len(set(seq[i:i+4]))==1:  # ４並び
                win[seq[i]] = 1
        return win

    def canmove(self, turn, inhand, board, prohmove):  # 全ての手
        allmove, winidx, loseidx, drawidx, noneidx = [], [], [], [], []
        if inhand[turn]:  # 持ち駒あり
            takepos = -1
            inhand[turn] -= 1  # 取る
            for placepos in range(8):
                if prohmove!=[takepos, placepos] and len(board[placepos])<3:
                    board[placepos].append(turn)  # 置く
                    win = self.judge(board)
                    idx = len(allmove)
                    if win==[0, 0]:
                        noneidx.append(idx)
                    elif win==[1, 1]:
                        drawidx.append(idx)
                    elif (turn==P1 and win==[1, 0]) or (turn==P2 and win==[0, 1]):
                        winidx.append(idx)
                    else:
                        loseidx.append(idx)
                    allmove.append([[takepos, placepos], inhand[:], [pcs[:] for pcs in board]])
                    board[placepos].pop()  # 元に戻す
            inhand[turn] += 1  # 元に戻す
        else:  # 持ち駒なし
            for takepos in range(8):
                pcs = board[takepos]
                if pcs and pcs[-1]==turn:
                    board[takepos].pop()  # 取る
                    canplace = [takepos-4 if takepos>3 else takepos+4, (takepos+1)%8, (takepos+7)%8]
                    for placepos in canplace:
                        if prohmove!=[takepos, placepos] and placepos!=takepos and len(board[placepos])<3:
                            board[placepos].append(turn)  # 置く
                            win = self.judge(board)
                            idx = len(allmove)
                            if win==[0, 0]:
                                noneidx.append(idx)
                            elif win==[1, 1]:
                                drawidx.append(idx)
                            elif (turn==P1 and win==[1, 0]) or (turn==P2 and win==[0, 1]):
                                winidx.append(idx)
                            else:
                                loseidx.append(idx)
                            allmove.append([[takepos, placepos], inhand[:], [pcs[:] for pcs in board]])
                            board[placepos].pop()  # 元に戻す
                    board[takepos].append(turn)  # 元に戻す
        return allmove, winidx, loseidx, drawidx, noneidx

    def xywh_center(self):
        w, h = CMSG_W, CMSG_H
        x, y = CMSG_X-w//2, CMSG_Y-h//2
        return x, y, w, h

    def xy_inhand(self, turn, dy=0):
        x, y = IH_X, IH_Y
        ht = 12 if self.ih[turn]>2 else self.ih[turn]*4
        return x, y-ht+dy

    def xywh_inhand(self, turn):
        w, h = IH_W, IH_H
        x, y = IH_X-w//2, IH_Y-h//2
        ht = 12 if self.ih[turn]>2 else self.ih[turn]*4
        return x, y, w, h, ht

    def xy_piece(self, pos, dy=0):
        x, y = OB_XYWH[pos][0], OB_XYWH[pos][1]
        pcs = self.bd[pos]
        ht = len(pcs)*4 if 2<pos<=6 else len(pcs)*3
        return x, y-ht+dy

    def xywh_piece(self, pos):
        w, h = OB_XYWH[pos][2], OB_XYWH[pos][3]
        x, y = OB_XYWH[pos][0]-w//2, OB_XYWH[pos][1]-h//2
        pcs = self.bd[pos]
        ht = len(pcs)*4 if 2<pos<=6 else len(pcs)*3
        return x, y, w, h, ht, pcs

    def se(self, n):
        pyxel.play(0, [n])

    def update(self):
        if self.st==ST_TITLE:  # タイトル
            self.cur = CUR_HAND
            if LMSG_X<pyxel.mouse_x<=LMSG_X+LMSG_W and LMSG_Y<pyxel.mouse_y<=LMSG_Y+LMSG_H:
                self.cur = CUR_FINGER
                if pyxel.btnr(pyxel.MOUSE_BUTTON_LEFT):  # 人間対人間
                    self.start()
                    self.init_piece()
                    self.vs = VS_MAN
                    self.st = ST_START
            if RMSG_X<pyxel.mouse_x<=RMSG_X+RMSG_W and RMSG_Y<pyxel.mouse_y<=RMSG_Y+RMSG_H:
                self.cur = CUR_FINGER
                if pyxel.btnr(pyxel.MOUSE_BUTTON_LEFT):  # 人間対コンピュータ
                    self.start()
                    self.init_piece()
                    self.vs = VS_COM
                    self.st = ST_START
            if pyxel.mouse_x!=self.mx or pyxel.mouse_y!=self.my:
                self.cnt = 0
                self.mx, self.my = pyxel.mouse_x, pyxel.mouse_y
            elif self.cnt<400:
                self.cnt += 1
            else:
                self.start()
                self.init_piece()
                self.vs = VS_DEMO
                self.st = ST_START

        elif self.st==ST_START:  # 前処理
            self.turn = 1-self.turn  # 交代
            self.allmove, self.winidx, self.loseidx, self.drawidx, self.noneidx = \
                    self.canmove(self.turn, self.ih, self.bd, self.prevmove if self.sb==SB_DONE else [-1,-1])  # 全ての手
            if not self.allmove and self.sb==SB_ENABLE:  # 打つ手なし
                self.sb = SB_MUST
            if self.sb==SB_MUST:
                self.cursor_x, self.cursor_y = CMSG_X, CMSG_Y+6
                if self.vs==VS_MAN or (self.vs==VS_COM and self.turn==P2):
                    pyxel.set_mouse_pos(self.cursor_x, self.cursor_y)
            elif self.ih[self.turn]:
                self.cursor_x, self.cursor_y = self.xy_inhand(self.turn, 4)
                if self.vs==VS_MAN or (self.vs==VS_COM and self.turn==P2):
                    pyxel.set_mouse_pos(self.cursor_x, self.cursor_y)
            if not self.allmove and self.sb!=SB_MUST:  # 打つ手なし
                self.win[1-self.turn] = 1
                self.cnt = 0
                if self.vs!=VS_DEMO:
                    self.se(3)  # 終了
                self.st = ST_END
            elif self.vs==VS_DEMO or (self.vs==VS_COM and self.turn==P1):
                self.st = ST_COM
            else:
                self.st = ST_TAKE

        elif self.st==ST_COM:  # コンピュータの手
            self.cur = CUR_HAND
            self.moveidx = -2
            if self.sb==SB_MUST or (self.sb==SB_ENABLE and pyxel.rndi(0,5)==0):
                self.moveidx = -1
            elif self.winidx:
                r = pyxel.rndi(0, len(self.winidx)-1)
                self.moveidx = self.winidx[r]
            elif self.sb==SB_ENABLE and pyxel.rndi(0,2)==0:
                self.moveidx = -1
            elif self.noneidx:
                r = pyxel.rndi(0, len(self.noneidx)-1)
                self.moveidx = self.noneidx[r]
            elif self.sb==SB_ENABLE:
                self.moveidx = -1
            elif self.drawidx:
                r = pyxel.rndi(0, len(self.drawidx)-1)
                self.moveidx = self.drawidx[r]
            elif self.loseidx:
                r = pyxel.rndi(0, len(self.loseidx)-1)
                self.moveidx = self.loseidx[r]
            self.mx, self.my = pyxel.mouse_x, pyxel.mouse_y
            self.cnt = 0
            self.st = ST_MOTION

        elif self.st==ST_MOTION:
            if self.vs==VS_DEMO and (pyxel.mouse_x!=self.mx or pyxel.mouse_y!=self.my or 
                        pyxel.btnr(pyxel.MOUSE_BUTTON_LEFT) or pyxel.btnr(pyxel.MOUSE_BUTTON_RIGHT)):
                self.start()
                self.cnt = 0
                self.st = ST_TITLE
            else:
                self.cnt+=1
                if self.moveidx==-1:  # セカンドベスト
                    if self.cnt==1:
                        self.cur = CUR_FINGER
                        self.cursor_x, self.cursor_y = CMSG_X, CMSG_Y+6
                    elif self.cnt==20:
                        if self.vs!=VS_DEMO:
                            self.se(2)  # セカンドベスト
                        self.cursor_x, self.cursor_y = CMSG_X, CMSG_Y+8
                        self.ih = self.previh[:]
                        self.bd = [pcs[:] for pcs in self.prevbd]
                        self.sb = SB_DONE
                    elif self.cnt>=30:
                        self.st = ST_START
                elif self.moveidx>=0:
                    if self.cnt==1:
                        self.cur = CUR_FINGER
                        self.previh = self.ih[:]
                        self.prevbd = [pcs[:] for pcs in self.bd]
                        takepos = self.allmove[self.moveidx][0][0]
                        if takepos>=0:  # 盤面から駒を取る
                            self.cursor_x, self.cursor_y = self.xy_piece(takepos, 4)

                    elif self.cnt==20:
                        if self.vs!=VS_DEMO:
                            self.se(0)  # 取る
                        self.cur = CUR_HOLD
                        placepos = self.allmove[self.moveidx][0][1]
                        self.cursor_x, self.cursor_y = self.xy_piece(placepos, 4)
                    elif self.cnt==40:
                        if self.vs!=VS_DEMO:
                            self.se(1)  # 置く
                        self.cur = CUR_FINGER
                        self.prevmove = self.allmove[self.moveidx][0][:]
                        self.ih = self.allmove[self.moveidx][1][:]
                        self.bd = [pcs[:] for pcs in self.allmove[self.moveidx][2]]
                    elif self.cnt>=50:
                        self.st = ST_JUDGE
            self.mx, self.my = pyxel.mouse_x, pyxel.mouse_y

        elif self.st==ST_TAKE:  # 駒を取る
            self.cur = CUR_HAND
            if self.sb in (SB_ENABLE, SB_MUST):  # セカンドベストを選択可
                x, y, w, h = self.xywh_center()
                if x<pyxel.mouse_x<=x+w and y<pyxel.mouse_y<=y+h:
                    self.cur = CUR_FINGER
                    if pyxel.btnr(pyxel.MOUSE_BUTTON_LEFT):  # セカンドベストを選択
                        self.se(2)  # セカンドベスト
                        self.ih = self.previh[:]
                        self.bd = [pcs[:] for pcs in self.prevbd]
                        self.sb = SB_DONE
                        self.st = ST_START
            if self.sb!=SB_MUST and self.st!=ST_START:
                if self.ih[self.turn]:  # 持ち駒あり
                    x, y, w, h, ht = self.xywh_inhand(self.turn)
                    if x<pyxel.mouse_x<=x+w and y-ht<pyxel.mouse_y<=y+h-ht:
                        self.cur = CUR_FINGER
                        if pyxel.btnr(pyxel.MOUSE_BUTTON_LEFT):  # 持ち駒から駒を取る
                            self.se(0)  # 取る
                            self.recboard()
                            self.ih[self.turn] -= 1
                            self.takepos = -1
                            self.st = ST_PLACE
                else:  # 持ち駒なし
                    for pos in range(8):
                        x, y, w, h, ht, pcs = self.xywh_piece(pos)
                        if x<pyxel.mouse_x<=x+w and y-ht<pyxel.mouse_y<=y+h-ht:
                            if pcs and pcs[-1]==self.turn:
                                self.cur = CUR_FINGER
                                if pyxel.btnr(pyxel.MOUSE_BUTTON_LEFT):  # 盤面から駒を取る
                                    self.se(0)  # 取る
                                    self.recboard()
                                    self.bd[pos].pop()
                                    self.takepos = pos
                                    self.st = ST_PLACE
                                break

        elif self.st==ST_PLACE:  # 駒を置く
            self.cur = CUR_HOLD
            rng = RMSG_X<pyxel.mouse_x<=RMSG_X+RMSG_W and RMSG_Y<pyxel.mouse_y<=RMSG_Y+RMSG_H
            if (rng and pyxel.btnr(pyxel.MOUSE_BUTTON_LEFT)) or pyxel.btnr(pyxel.MOUSE_BUTTON_RIGHT):  # 取り直し
                self.se(1)  # 置く
                if self.takepos==-1:
                    self.ih[self.turn] += 1
                else:
                    self.bd[self.takepos].append(self.turn)
                if self.sb==SB_ENABLE:
                    self.sb = SB_DISABLE  # 取り直し後のセカンドベストは不可
                self.st = ST_TAKE
            elif rng:
                self.cur = CUR_FINGER
            if self.st!=ST_TAKE and self.cur!=CUR_FINGER:
                if self.takepos==-1:
                    canplace = list(range(8))
                else:
                    canplace = [self.takepos-4 if self.takepos>3 else self.takepos+4, (self.takepos+1)%8, (self.takepos+7)%8]
                for pos in canplace:
                    x, y, w, h, ht, pcs = self.xywh_piece(pos)
                    if x<pyxel.mouse_x<=x+w and y-ht<pyxel.mouse_y<=y+h-ht:
                        if self.sb==SB_DONE and self.prevmove==[self.takepos, pos]:  # セカンドベストで置けない
                            self.cur = CUR_CROSS
                        elif pos!=self.takepos and len(pcs)<3:
                            self.cur = CUR_PLACE
                            if pyxel.btnr(pyxel.MOUSE_BUTTON_LEFT):  # 駒を置く
                                self.se(1)  # 置く
                                self.prevmove = [self.takepos, pos]
                                self.bd[pos].append(self.turn)
                                self.st = ST_JUDGE
                            break

        elif self.st==ST_JUDGE:  # 判定
            self.win = self.judge(self.bd)
            self.st = ST_START
            if self.sb==SB_DONE:
                self.sb = SB_DISABLE
            elif self.sb==SB_DISABLE:
                self.sb = SB_ENABLE
            if self.win[1-self.turn]:
                self.cnt = 0
                if self.vs!=VS_DEMO:
                    self.se(3)  # 終了
                self.st = ST_END  # 自滅
            elif self.win[self.turn]:
                if self.sb==SB_ENABLE:
                    self.sb = SB_MUST  # 次はセカンドベスト必須
                else:
                    self.cnt = 0
                    if self.vs!=VS_DEMO:
                        self.se(3)  # 終了
                    self.st = ST_END

        elif self.st==ST_END:  # 終了
            self.cur = CUR_HAND
            if LMSG_X<pyxel.mouse_x<=LMSG_X+LMSG_W and LMSG_Y<pyxel.mouse_y<=LMSG_Y+LMSG_H:
                self.cur = CUR_FINGER
                if pyxel.btnr(pyxel.MOUSE_BUTTON_LEFT):  # タイトル
                    self.start()
                    self.cnt = 0
                    self.st = ST_TITLE
            if RMSG_X<pyxel.mouse_x<=RMSG_X+RMSG_W and RMSG_Y<pyxel.mouse_y<=RMSG_Y+RMSG_H:
                self.cur = CUR_FINGER
                if pyxel.btnr(pyxel.MOUSE_BUTTON_LEFT):  # もう一度
                    self.start()
                    self.init_piece()
                    self.st = ST_START
            if self.vs==VS_DEMO:
                if self.cnt<200:  # デモ
                    self.cnt += 1
                else:
                    self.start()
                    self.cnt = 0
                    self.st = ST_TITLE

    def draw_board(self):  # ボード
        for pos in range(7):  # 隣線
            x1, y1 = OB_XYWH[pos  ][0], OB_XYWH[pos  ][1]
            x2, y2 = OB_XYWH[pos+1][0], OB_XYWH[pos+1][1]
            c = COL[self.turn][0] if self.st==ST_PLACE and (self.takepos==-1 or self.takepos in (pos, pos+1)) else 0
            pyxel.line(x1, y1, x2, y2, c)
        c = COL[self.turn][0] if self.st==ST_PLACE and (self.takepos==-1 or self.takepos in (0, 7)) else 0
        pyxel.line(OB_XYWH[7][0], OB_XYWH[7][1], OB_XYWH[0][0], OB_XYWH[0][1], c)
        for pos in range(4):  # 対角線
            x1, y1 = OB_XYWH[pos  ][0], OB_XYWH[pos  ][1]
            x2, y2 = OB_XYWH[pos+4][0], OB_XYWH[pos+4][1]
            c = COL[self.turn][0] if self.st==ST_PLACE and self.takepos in (pos, pos+4) else 0
            pyxel.line(x1, y1, x2, y2, c)
        for pos in range(8):  # 周囲6大円
            x, y, w, h, _, _ = self.xywh_piece(pos)
            pyxel.elli(x-2, y-2, w+4, h+4, 0)
        for pos in range(8):  # 周囲6小円
            x, y, w, h, _, _ = self.xywh_piece(pos)
            pyxel.elli(x, y, w, h, 1)
        x, y, w, h = self.xywh_center()
        pyxel.elli(x-2, y-2, w+4, h+4, 0)  # 中央大円

    def draw_center(self):  # 中央メッセージ
        x, y, w, h = self.xywh_center()
        if self.st in (ST_TAKE, ST_MOTION) and self.sb in (SB_ENABLE, SB_MUST):  # セカンドベスト可／必須
            pyxel.elli(x, y  , w, h, 1)  # 中央小円
            pyxel.elli(x, y-1, w, h, 1)
            c = 5 if self.sb==SB_ENABLE else (pyxel.frame_count//4)%5+1  # 色(セカンドベスト可／必須：点滅)
            pyxel.elli(x, y-2, w, h, c)
            pyxel.blt(CMSG_X-16, CMSG_Y-16-2, 0, 0, 0, 32, 32, 0)
        else:
            if self.st==ST_END:
                c = (pyxel.frame_count//4)%5+1  # 色（終了：点滅）
            elif self.sb==SB_DONE:
                c = 0  # （セカンドベスト済）
            else:
                c = 1  # （セカンドベスト不可）
            x, y, w, h = self.xywh_center()
            pyxel.elli(x, y, w, h, c)  # 中央小円
            if self.st==ST_END:  # メッセージ
                if self.win[P1] and self.win[P2]:
                    pyxel.blt(CMSG_X-16, CMSG_Y-16, 0, 96, 0, 32, 32, 0)  # 引き分け
                elif self.win[P1]:
                    pyxel.blt(CMSG_X-16, CMSG_Y-16, 0, 32, 0, 32, 32, 0)  # P1赤のかち
                elif  self.win[P2]:
                    pyxel.blt(CMSG_X-16, CMSG_Y-16, 0, 64, 0, 32, 32, 0)  # P2白のかち
            else:
                pyxel.blt(CMSG_X-16, CMSG_Y-16, 0, 0, 0, 32, 32, 0)  # セカンドベスト不可

    def draw_piece(self):  # ボード上の駒
        for pos in range(8):
            x, y, w, h, _, pcs = self.xywh_piece(pos)
            ht = 0
            for i, pc in enumerate(self.bd[pos]):
                c1, c2 = COL[pc][0], COL[pc][1]
                pyxel.elli(x, y-ht  , w, h, c2)
                pyxel.elli(x, y-ht-1, w, h, c2)
                ht += 2
                if 2<pos<=6:
                    pyxel.elli(x, y-ht, w, h, c2)
                    ht += 1
                if i==len(pcs)-1:
                    pyxel.elli(x, y-ht, w, h, c1)
                else:
                    pyxel.elli(x, y-ht, w, h, 0)
                    ht += 1

    def draw_inhand(self):  # 持ち駒（順番）
        x, y, w, h, _ = self.xywh_inhand(self.turn)
        c1, c2 = COL[self.turn][0], COL[self.turn][1]
        pyxel.ellib(x-2, y-2, w+4, h+4, 10 if self.st==ST_TITLE else c1)
        if self.ih[self.turn]>0:
            pyxel.elli(x, y  , w, h, c2)
            pyxel.elli(x, y-1, w, h, c2)
            pyxel.elli(x, y-2, w, h, c2)
        if self.ih[self.turn]>1:
            pyxel.elli(x ,y-3, w, h, 0)
            pyxel.elli(x, y-4, w, h, c2)
            pyxel.elli(x, y-5, w, h, c2)
            pyxel.elli(x, y-6, w, h, c2)
        if self.ih[self.turn]>2 and self.st!=ST_PLACE and self.cur!=CUR_HOLD:
            pyxel.elli(x ,y-7, w, h, 0)
            pyxel.elli(x, y-8, w, h, c2)
            pyxel.elli(x, y-9, w, h, c2)
            pyxel.elli(x, y-10, w, h, c2)
        if self.ih[self.turn]==1:
            pyxel.elli(x, y-3, w, h, c1)
        elif self.ih[self.turn]==2 or (self.ih[self.turn]>2 and (self.st==ST_PLACE or self.cur==CUR_HOLD)):
            pyxel.elli(x, y-7, w, h, c1)
        elif self.ih[self.turn]>2 and self.st!=ST_PLACE and self.cur!=CUR_HOLD:
            pyxel.elli(x, y-11, w, h, c1)
        if self.vs==VS_DEMO and self.st!=ST_TITLE:
            pyxel.text(42, 132, 'Demo', 10)
        elif self.st!=ST_TITLE and self.st!=ST_END:
            if self.vs==VS_MAN:
                pyxel.text(42, 132, 'Turn', 10)
            elif self.turn==P1:
                pyxel.text(34, 132, 'Computer', 10)
            else:
                pyxel.text(38, 132, 'Player', 10)

    def draw_left(self):  # 左円メッセージ
        #pyxel.rectb(LMSG_X, LMSG_Y, LMSG_W, LMSG_H, 7)
        if self.st==ST_TITLE:
            pyxel.text(LMSG_X+6, LMSG_Y+3, 'Human', 10)
            pyxel.text(LMSG_X+12, LMSG_Y+10, 'vs', 10)
            pyxel.text(LMSG_X+6, LMSG_Y+17, 'Human', 10)
        elif self.st==ST_END:
            pyxel.text(LMSG_X+6, LMSG_Y+10, 'Title', 10)

    def draw_right(self):  # 右円メッセージ
        #pyxel.rectb(RMSG_X, RMSG_Y, RMSG_W, RMSG_H, 7)
        if self.st==ST_TITLE:
            pyxel.text(RMSG_X+0, RMSG_Y+3, 'Computer', 10)
            pyxel.text(RMSG_X+12, RMSG_Y+10, 'vs', 10)
            pyxel.text(RMSG_X+6, RMSG_Y+17, 'Human', 10)
        elif self.st==ST_PLACE:
            pyxel.text(RMSG_X+8, RMSG_Y+10, 'Undo', 10)
        elif self.st==ST_END:
            pyxel.text(RMSG_X+8, RMSG_Y+7, 'Play', 10)
            pyxel.text(RMSG_X+6, RMSG_Y+14, 'Again', 10)

    def draw_cross(self, x, y):  # 置ける位置
        cnt = pyxel.frame_count % 60
        c = COL[self.turn][2]
        if cnt in (0,1,2,3,11,12,13):
            pyxel.line(x-1, y, x+1, y, c)
            pyxel.line(x, y-1, x, y+1, c)
        elif cnt in (4,5,6,7,8,9,10):
            pyxel.line(x-2, y, x+2, y, c)
            pyxel.line(x, y-2, x, y+2, c)

    def draw_path(self):
        pos = self.prevmove[1]  #　置いた位置
        if pos!=-1 and self.sb!=SB_DONE:
            x, y, w, h, ht, pcs = self.xywh_piece(pos)
            x += w*3//4
            y += h*3//4
            c = COL[P2 if pcs and pcs[-1]==P2 else P1][1]
            pyxel.line(x-1, y-ht, x-3, y-ht, c)
            pyxel.line(x, y-ht-1, x, y-ht-2, c)
        if self.st==ST_TAKE:  # 置ける位置
            if self.sb in (SB_ENABLE, SB_MUST):
                self.draw_cross(CMSG_X-9, CMSG_Y-12)
            if self.sb!=SB_MUST:
                if self.ih[self.turn]:  # 持ち駒あり
                    x, y, _, _, ht = self.xywh_inhand(self.turn)
                    self.draw_cross(x+6, y-ht+6)
                else:  # 持ち駒なし
                    for pos in range(8):
                        x, y, _, _, ht, pcs = self.xywh_piece(pos)
                        if pcs and pcs[-1]==self.turn:
                            self.draw_cross(x+5, y-ht+5)

    def draw_cursor(self):  # カーソル
        if not self.st in (ST_START, ST_COM, ST_MOTION, ST_JUDGE):
            self.cursor_x, self.cursor_y = pyxel.mouse_x, pyxel.mouse_y
        if self.cur==CUR_HAND:
            pyxel.blt(self.cursor_x-5, self.cursor_y-1, 0, 0, 32 if self.turn==P1 else 48, 12, 16, 0)
        elif self.cur==CUR_FINGER:
            pyxel.blt(self.cursor_x-5, self.cursor_y-1, 0, 16, 32 if self.turn==P1 else 48, 12, 16, 0)
        elif self.cur==CUR_HOLD:
            pyxel.blt(self.cursor_x-6, self.cursor_y-1, 0, 32, 32 if self.turn==P1 else 48, 12, 16, 0)
        elif self.cur==CUR_PLACE:
            pyxel.blt(self.cursor_x-5, self.cursor_y-5, 0, 48, 32 if self.turn==P1 else 48, 12, 12, 0)
        elif self.cur==CUR_CROSS:
            pyxel.blt(self.cursor_x-5, self.cursor_y-5, 0, 64, 32 if self.turn==P1 else 48, 12, 12, 0)

    def draw(self):
        pyxel.cls(3)
        self.draw_board()  # ボード
        self.draw_center()  # 中央メッセージ
        self.draw_piece()  # ボード上の駒
        self.draw_inhand()  # 持ち駒（順番）
        self.draw_left()  # 左メッセージ
        self.draw_right()  # 右メッセージ
        self.draw_path()  # 軌跡
        self.draw_cursor()  # カーソル

App()
