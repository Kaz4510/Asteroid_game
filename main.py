import asyncio
import sys

import pygame

from asteroid import Asteroid
from asteroidfield import AsteroidField
from constants import (
    GAME_OVER_INFO_FONT_SIZE,
    GAME_OVER_TITLE_FONT_SIZE,
    LINE_WIDTH,
    SCORE_FONT_SIZE,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
)
from logger import log_event, log_state
from player import Player
from shot import Shot

ON_WEB = sys.platform == "emscripten"


async def play_round(
    screen: pygame.Surface, clock: pygame.time.Clock, score_font: pygame.font.Font
) -> int | None:
    # Returns the final score when the player dies, or None if the player quit
    dt = 0.0
    score = 0

    updatable = pygame.sprite.Group()
    drawable = pygame.sprite.Group()
    asteroids = pygame.sprite.Group()
    shots = pygame.sprite.Group()

    AsteroidField.containers = updatable
    Asteroid.containers = (asteroids, updatable, drawable)
    Player.containers = (updatable, drawable)
    Shot.containers = (shots, updatable, drawable)

    player = Player(x=SCREEN_WIDTH / 2, y=SCREEN_HEIGHT / 2)
    asteroid_field = AsteroidField()

    while True:
        log_state()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return None

        screen.fill("black")
        updatable.update(dt)

        for asteroid in asteroids:
            if player.collides_with(asteroid):
                log_event("player_hit")
                return score
            for shot in shots:
                if shot.collides_with(asteroid):
                    log_event("asteroid_shot")
                    score += 1
                    asteroid.split()
                    shot.kill()

        for sprite in drawable:
            sprite.draw(screen)

        score_surface = score_font.render(f"Score: {score}", True, "white")
        screen.blit(score_surface, (10, 10))

        pygame.display.flip()

        dt = clock.tick(60) / 1000
        await asyncio.sleep(0)  # <-- yields to the browser event loop


async def game_over_screen(
    screen: pygame.Surface,
    clock: pygame.time.Clock,
    title_font: pygame.font.Font,
    info_font: pygame.font.Font,
    score: int,
    best_score: int,
) -> bool:
    # Returns True to play again, False to quit
    button_rect = pygame.Rect(0, 0, 280, 64)
    button_rect.center = (SCREEN_WIDTH // 2, int(SCREEN_HEIGHT * 0.72))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                return True
            if (
                event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
                and button_rect.collidepoint(event.pos)
            ):
                return True

        screen.fill("black")

        title = title_font.render("GAME OVER", True, "white")
        screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, int(SCREEN_HEIGHT * 0.32))))

        score_text = info_font.render(f"Score: {score}", True, "white")
        screen.blit(score_text, score_text.get_rect(center=(SCREEN_WIDTH // 2, int(SCREEN_HEIGHT * 0.47))))

        best_text = info_font.render(f"Best this session: {best_score}", True, "white")
        screen.blit(best_text, best_text.get_rect(center=(SCREEN_WIDTH // 2, int(SCREEN_HEIGHT * 0.55))))

        hovering = button_rect.collidepoint(pygame.mouse.get_pos())
        if hovering:
            pygame.draw.rect(screen, "white", button_rect)
        else:
            pygame.draw.rect(screen, "white", button_rect, LINE_WIDTH)
        label = info_font.render("Play Again", True, "black" if hovering else "white")
        screen.blit(label, label.get_rect(center=button_rect.center))

        hint = info_font.render("or press Enter", True, "grey")
        screen.blit(hint, hint.get_rect(center=(SCREEN_WIDTH // 2, int(SCREEN_HEIGHT * 0.83))))

        pygame.display.flip()

        clock.tick(60)
        await asyncio.sleep(0)  # <-- yields to the browser event loop


async def main() -> None:
    pygame.init()
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    score_font = pygame.font.Font(None, SCORE_FONT_SIZE)
    title_font = pygame.font.Font(None, GAME_OVER_TITLE_FONT_SIZE)
    info_font = pygame.font.Font(None, GAME_OVER_INFO_FONT_SIZE)
    best_score = 0

    while True:
        score = await play_round(screen, clock, score_font)
        if score is None:
            break
        best_score = max(best_score, score)
        if not await game_over_screen(screen, clock, title_font, info_font, score, best_score):
            break

    if ON_WEB:
        # No window to close in the browser: leave a goodbye frame on the canvas
        screen.fill("black")
        goodbye = info_font.render("Thanks for playing! Refresh the page to play again.", True, "white")
        screen.blit(goodbye, goodbye.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)))
        pygame.display.flip()
    else:
        pygame.quit()


if __name__ == "__main__":
    asyncio.run(main())
