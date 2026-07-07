import asyncio

import pygame

from asteroid import Asteroid
from asteroidfield import AsteroidField
from constants import SCORE_FONT_SIZE, SCREEN_HEIGHT, SCREEN_WIDTH
from logger import log_event, log_state
from player import Player
from shot import Shot


async def main():
    pygame.init()
    clock = pygame.time.Clock()
    dt = 0.0
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    font = pygame.font.Font(None, SCORE_FONT_SIZE)
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
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit()
                return

        screen.fill("black")
        updatable.update(dt)

        for asteroid in asteroids:
            if player.collides_with(asteroid):
                log_event("player_hit")
                print("Game Over!")
                pygame.quit()
                return
            for shot in shots:
                if shot.collides_with(asteroid):
                    log_event("asteroid_shot")
                    score += 1
                    asteroid.split()
                    shot.kill()

        for sprite in drawable:
            sprite.draw(screen)

        score_surface = font.render(f"Score: {score}", True, "white")
        screen.blit(score_surface, (10, 10))

        pygame.display.flip()

        dt = clock.tick(60) / 1000
        await asyncio.sleep(0)  # <-- yields to the browser event loop


if __name__ == "__main__":
    asyncio.run(main())
