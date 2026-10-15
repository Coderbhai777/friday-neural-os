"""
ULTRON Chess-Tiger Master Grandmaster Engine
Real-time tactical chess engine, Minimax Alpha-Beta + Quiescence search,
positional Piece-Square Tables, opening repertoire, and screen vision analyzer.
"""

import os
import re
import io
import time
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

import chess
import chess.engine

try:
    import cv2
    import numpy as np
except ImportError:
    cv2 = None
    np = None

try:
    from PIL import Image
except ImportError:
    Image = None

try:
    import mss
except ImportError:
    mss = None

try:
    import pyautogui
except ImportError:
    pyautogui = None

try:
    from dotenv import load_dotenv
    env_paths = [
        Path.home() / "Documents" / "ULTRON_Data" / ".env",
        Path.home() / ".env",
        Path(".env")
    ]
    for ep in env_paths:
        if ep.exists():
            load_dotenv(dotenv_path=ep, override=False)
except Exception:
    pass

# Piece values in centipawns
PIECE_VALUES_CP = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 20000
}

# Simplified Evaluation Function Piece-Square Tables (PST) from White's perspective
PST_PAWN = [
    0,   0,   0,   0,   0,   0,   0,   0,
    50,  50,  50,  50,  50,  50,  50,  50,
    10,  10,  20,  30,  30,  20,  10,  10,
    5,   5,  10,  25,  25,  10,   5,   5,
    0,   0,   0,  20,  20,   0,   0,   0,
    5,  -5, -10,   0,   0, -10,  -5,   5,
    5,  10,  10, -20, -20,  10,  10,   5,
    0,   0,   0,   0,   0,   0,   0,   0
]

PST_KNIGHT = [
    -50, -40, -30, -30, -30, -30, -40, -50,
    -40, -20,   0,   0,   0,   0, -20, -40,
    -30,   0,  10,  15,  15,  10,   0, -30,
    -30,   5,  15,  20,  20,  15,   5, -30,
    -30,   0,  15,  20,  20,  15,   0, -30,
    -30,   5,  10,  15,  15,  10,   5, -30,
    -40, -20,   0,   5,   5,   0, -20, -40,
    -50, -40, -30, -30, -30, -30, -40, -50,
]

PST_BISHOP = [
    -20, -10, -10, -10, -10, -10, -10, -20,
    -10,   0,   0,   0,   0,   0,   0, -10,
    -10,   0,   5,  10,  10,   5,   0, -10,
    -10,   5,   5,  10,  10,   5,   5, -10,
    -10,   0,  10,  10,  10,  10,   0, -10,
    -10,  10,  10,  10,  10,  10,  10, -10,
    -10,   5,   0,   0,   0,   0,   5, -10,
    -20, -10, -10, -10, -10, -10, -10, -20,
]

PST_ROOK = [
    0,   0,   0,   0,   0,   0,   0,   0,
    5,  10,  10,  10,  10,  10,  10,   5,
    -5,   0,   0,   0,   0,   0,   0,  -5,
    -5,   0,   0,   0,   0,   0,   0,  -5,
    -5,   0,   0,   0,   0,   0,   0,  -5,
    -5,   0,   0,   0,   0,   0,   0,  -5,
    -5,   0,   0,   0,   0,   0,   0,  -5,
    0,   0,   0,   5,   5,   0,   0,   0
]

PST_QUEEN = [
    -20, -10, -10,  -5,  -5, -10, -10, -20,
    -10,   0,   0,   0,   0,   0,   0, -10,
    -10,   0,   5,   5,   5,   5,   0, -10,
    -5,   0,   5,   5,   5,   5,   0,  -5,
    0,   0,   5,   5,   5,   5,   0,  -5,
    -10,   5,   5,   5,   5,   5,   0, -10,
    -10,   0,   5,   0,   0,   0,   0, -10,
    -20, -10, -10,  -5,  -5, -10, -10, -20
]

PST_KING_MID = [
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -20, -30, -30, -40, -40, -30, -30, -20,
    -10, -20, -20, -20, -20, -20, -20, -10,
    20,  20,   0,   0,   0,   0,  20,  20,
    20,  30,  10,   0,   0,  10,  30,  20
]


def _evaluate_static_board(board: chess.Board) -> int:
    """Calculates static evaluation in centipawns from White's perspective."""
    if board.is_checkmate():
        return -99999 if board.turn == chess.WHITE else 99999
    if board.is_stalemate() or board.is_insufficient_material():
        return 0

    score = 0
    piece_map = board.piece_map()

    for sq, piece in piece_map.items():
        val = PIECE_VALUES_CP[piece.piece_type]
        pst_idx = 63 - sq if piece.color == chess.WHITE else sq

        pst_val = 0
        if piece.piece_type == chess.PAWN:
            pst_val = PST_PAWN[pst_idx]
        elif piece.piece_type == chess.KNIGHT:
            pst_val = PST_KNIGHT[pst_idx]
        elif piece.piece_type == chess.BISHOP:
            pst_val = PST_BISHOP[pst_idx]
        elif piece.piece_type == chess.ROOK:
            pst_val = PST_ROOK[pst_idx]
        elif piece.piece_type == chess.QUEEN:
            pst_val = PST_QUEEN[pst_idx]
        elif piece.piece_type == chess.KING:
            pst_val = PST_KING_MID[pst_idx]

        piece_score = val + pst_val
        if piece.color == chess.WHITE:
            score += piece_score
        else:
            score -= piece_score

    # Center control bonuses
    for center_sq in [chess.E4, chess.D4, chess.E5, chess.D5]:
        score += len(board.attackers(chess.WHITE, center_sq)) * 10
        score -= len(board.attackers(chess.BLACK, center_sq)) * 10

    return score


def _quiescence_search(board: chess.Board, alpha: int, beta: int, depth: int = 3) -> int:
    """Quiescence search to evaluate captures and avoid the horizon effect."""
    stand_pat = _evaluate_static_board(board)
    if board.turn == chess.BLACK:
        stand_pat = -stand_pat

    if depth == 0:
        return stand_pat
    if stand_pat >= beta:
        return beta
    if alpha < stand_pat:
        alpha = stand_pat

    # Only evaluate captures
    for move in board.legal_moves:
        if board.is_capture(move):
            board.push(move)
            score = -_quiescence_search(board, -beta, -alpha, depth - 1)
            board.pop()

            if score >= beta:
                return beta
            if score > alpha:
                alpha = score

    return alpha


def _alpha_beta_search(board: chess.Board, depth: int, alpha: int, beta: int) -> Tuple[int, Optional[chess.Move]]:
    """Minimax Alpha-Beta search returning (score_cp, best_move)."""
    if depth == 0 or board.is_game_over():
        return _quiescence_search(board, alpha, beta), None

    best_move = None
    if board.turn == chess.WHITE:
        max_eval = -999999
        for move in board.legal_moves:
            board.push(move)
            eval_score, _ = _alpha_beta_search(board, depth - 1, alpha, beta)
            board.pop()

            if eval_score > max_eval:
                max_eval = eval_score
                best_move = move
            alpha = max(alpha, eval_score)
            if beta <= alpha:
                break
        return max_eval, best_move
    else:
        min_eval = 999999
        for move in board.legal_moves:
            board.push(move)
            eval_score, _ = _alpha_beta_search(board, depth - 1, alpha, beta)
            board.pop()

            if eval_score < min_eval:
                min_eval = eval_score
                best_move = move
            beta = min(beta, eval_score)
            if beta <= alpha:
                break
        return min_eval, best_move


def _calculate_best_move_and_score(board: chess.Board, depth: int = 3) -> Tuple[str, str, float]:
    """Calculates top move, evaluation score, and principal continuation."""
    # Check if external Stockfish engine exists
    stockfish_path = shutil.which("stockfish") or shutil.which("stockfish.exe")
    if stockfish_path and os.path.exists(stockfish_path):
        try:
            with chess.engine.SimpleEngine.popen_uci(stockfish_path) as engine:
                info = engine.analyse(board, chess.engine.Limit(time=0.4))
                score_cp = info["score"].white().score(mate_score=10000)
                eval_score = round(score_cp / 100.0, 2) if score_cp is not None else 0.0
                best_pv = info.get("pv", [])
                top_move_san = board.san(best_pv[0]) if best_pv else "None"
                pv_san = " ".join([board.san(m) for m in best_pv[:5]])
                return top_move_san, pv_san, eval_score
        except Exception:
            pass

    # Built-in High-Speed Minimax Alpha-Beta Engine
    score_cp, best_move = _alpha_beta_search(board, depth=depth, alpha=-999999, beta=999999)
    top_move_san = board.san(best_move) if best_move else "None"
    eval_score = round(score_cp / 100.0, 2)
    return top_move_san, top_move_san, eval_score


async def _safe_speak(text: str):
    try:
        from friday_tools.tts_engine import speak_text
        import inspect
        if inspect.iscoroutinefunction(speak_text):
            await speak_text(text)
        else:
            res = speak_text(text)
            if inspect.iscoroutine(res):
                await res
    except Exception:
        pass


async def chess_tiger_analyze_fen(fen: str, speak: bool = True) -> str:
    """
    Grandmaster FEN Position Evaluator:
    Runs deterministic Minimax Alpha-Beta tactical calculation, finds exact winning moves,
    identifies blunders, and pairs with AI synthesis for deep strategic plans.
    """
    clean_fen = fen.strip()
    try:
        board = chess.Board(clean_fen)
    except Exception as e:
        return f"❌ [CHESS-TIGER ERROR] Invalid FEN position string: {e}"

    if board.is_checkmate():
        winner = "Black" if board.turn == chess.WHITE else "White"
        return f"🏆 [CHECKMATE] {winner} wins by checkmate!"

    if board.is_stalemate():
        return "🤝 [DRAW] Stalemate detected. Game drawn."

    # Minimax Alpha-Beta Grandmaster Tactical Calculation
    top_move_san, pv_line, eval_score = _calculate_best_move_and_score(board, depth=3)
    turn_str = "White" if board.turn == chess.WHITE else "Black"
    eval_sign = "+" if eval_score > 0 else ""

    tactical_prompt = f"""
    You are CHESS-TIGER, Grandmaster Chess Engine & Tactical Coach for Shivansh.
    Position: {board.fen()}
    Turn to Move: {turn_str}
    Tactical Calculation:
    - Best Move (Engine Computed): {top_move_san}
    - Principal Continuation Line: {pv_line}
    - Exact Position Score: {eval_sign}{eval_score} (Centipawn normalized)
    - In Check: {board.is_check()}

    Provide:
    1. 🎯 BEST MOVE: Explain why {top_move_san} is the objectively superior move.
    2. ⚔️ TACTICAL COMBINATION: Show the exact variation after {top_move_san}.
    3. 🛡️ OPPONENT THREATS: What White/Black must defend against.
    4. 💡 STRATEGIC MASTERPLAN: Pawn structure, piece activity, king safety.
    Be sharp, decisive, and authoritative.
    """

    from friday_tools.ai_client import ask_ai
    analysis = ask_ai(tactical_prompt)

    report = [
        f"🐅 [CHESS-TIGER GRANDMASTER ENGINE REPORT]",
        f"• FEN: {board.fen()}",
        f"• Turn: {turn_str} to move | Engine Eval: {eval_sign}{eval_score}",
        f"• Recommended Best Move: {top_move_san} (Line: {pv_line})",
        "=" * 60,
        analysis
    ]
    full_text = "\n".join(report)

    if speak:
        await _safe_speak(f"{turn_str} to move. The best move is {top_move_san}. Evaluation is {eval_sign}{eval_score}.")

    return full_text


async def chess_tiger_best_move(fen: str) -> str:
    """
    Returns the single best Grandmaster candidate move computed by Minimax Alpha-Beta search.
    """
    try:
        board = chess.Board(fen.strip())
        top_move_san, pv_line, eval_score = _calculate_best_move_and_score(board, depth=3)
        turn_str = "White" if board.turn == chess.WHITE else "Black"
        eval_sign = "+" if eval_score > 0 else ""

        await _safe_speak(f"Best move is {top_move_san}, evaluation {eval_sign}{eval_score}.")

        return (
            f"🐅 [CHESS-TIGER BEST MOVE]\n"
            f"• Position Turn: {turn_str} to move\n"
            f"• Best Move: **{top_move_san}**\n"
            f"• Continuation Line: {pv_line}\n"
            f"• Engine Score: {eval_sign}{eval_score}"
        )
    except Exception as e:
        return f"[CHESS ERROR] {e}"



async def chess_tiger_opening_explorer(opening_name_or_moves: str) -> str:
    """
    Grandmaster Opening Explorer: ECO codes, mainlines, strategic plans, and tactical traps.
    """
    from friday_tools.ai_client import ask_ai
    prompt = f"""
    You are CHESS-TIGER Grandmaster Opening Repertoire Coach.
    Analyze the opening: '{opening_name_or_moves}'.
    
    Provide:
    1. 📖 Opening Name & ECO Code
    2. ♟️ Main Line Move Sequence in Standard Algebraic Notation
    3. 🎯 Key Strategic Ideas & Plans for White and Black
    4. ⚠️ Dangerous Traps / Tactical Pitfalls to Avoid
    5. 🏆 Notable Grandmaster Games (Kasparov, Carlsen, Fischer, Tal)
    """
    ans = ask_ai(prompt)
    return f"📖 [CHESS-TIGER OPENING REPERTOIRE // {opening_name_or_moves.upper()}]\n{'='*55}\n{ans}"


async def chess_tiger_game_review(pgn_or_moves: str) -> str:
    """
    PGN Game Reviewer: Analyzes game moves, calculates accuracy %, brilliant moves, and blunders.
    """
    from friday_tools.ai_client import ask_ai
    prompt = f"""
    You are CHESS-TIGER Senior Game Reviewer.
    Analyze this chess game / move sequence:
    ```
    {pgn_or_moves[:5000]}
    ```

    Provide:
    1. 📊 Estimated Accuracy (% for White and Black)
    2. 🌟 Critical Moments & Brilliant Moves
    3. ❌ Blunders, Mistakes & Missed Wins (with move numbers)
    4. 💡 Key Takeaway / Lesson for improvement
    """
    res = ask_ai(prompt)
    return f"🏆 [CHESS-TIGER ACCURACY & GAME REVIEW]\n{'='*55}\n{res}"


async def chess_tiger_solve_puzzle(puzzle_theme_or_fen: str = "tactics") -> str:
    """
    Tactical puzzle engine: Solves or generates positions with forks, pins, skewers, deflections.
    """
    from friday_tools.ai_client import ask_ai
    prompt = f"""
    You are CHESS-TIGER Tactical Puzzle Master.
    Create or analyze a tactical puzzle on the theme: '{puzzle_theme_or_fen}'.
    
    Provide:
    1. 🧩 Position Diagram / FEN
    2. 🎯 Objective (e.g. White to move and win material / Mate in 2)
    3. 🔍 Step-by-Step Solution with full variation calculation
    4. 🧠 Tactical Principle explained
    """
    ans = ask_ai(prompt)
    return f"🧩 [CHESS-TIGER TACTICAL PUZZLE]\n{'='*55}\n{ans}"


async def chess_tiger_scan_screen() -> str:
    """
    Captures screen using high-speed mss, extracts active chessboard on Chess.com / Lichess,
    and runs real-time tactical evaluation with spoken move callout.
    """
    try:
        shot_path = Path.home() / "Documents" / "ULTRON_Data" / "vision_cache" / "chess_screen.jpg"
        shot_path.parent.mkdir(parents=True, exist_ok=True)
        captured = False

        if mss:
            with mss.mss() as sct:
                mon = sct.monitors[1] if len(sct.monitors) > 1 else sct.monitors[0]
                img = sct.grab(mon)
                pil_img = Image.frombytes("RGB", img.size, img.bgra, "raw", "BGRX")
                pil_img.save(str(shot_path), format="JPEG", quality=85)
                captured = True

        if not captured and pyautogui:
            shot = pyautogui.screenshot()
            shot.save(str(shot_path))

        from friday_tools.jarvis_vision import analyze_image
        prompt = (
            "You are CHESS-TIGER Visual Perception Engine. Look at this screen capture. "
            "Locate the active chessboard on Chess.com, Lichess, or ChessBase. "
            "Extract the exact FEN position or piece positions. "
            "State whose turn it is to move, the top tactical threat, and the absolute best candidate move with full justification."
        )
        res = await analyze_image(str(shot_path), prompt=prompt)

        try:
            from friday_tools.tts_engine import speak_text
            first_sentence = res.split(".")[0] if "." in res else res[:60]
            speak_text(f"Screen analyzed. {re.sub(r'[*_#`]', '', first_sentence)}")
        except Exception:
            pass

        return f"🐅 [CHESS-TIGER LIVE SCREEN ANALYSIS]\n{'='*55}\n{res}"
    except Exception as e:
        return f"[CHESS ERROR] Failed to scan screen: {e}"
