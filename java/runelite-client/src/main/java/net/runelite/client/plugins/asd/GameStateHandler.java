package net.runelite.client.plugins.asd;

import javax.inject.Inject;
import lombok.extern.slf4j.Slf4j;
import net.runelite.api.Client;
import net.runelite.api.GameState;
import java.util.Map;

@Slf4j
public class GameStateHandler implements RequestHandler {
    @Inject
    private Client client;

    @Override
    public Object handle(String function, Map<String, Object> params) {
        switch (function) {
            case "gametick":
                return handleGameTickRequest();
            case "zoom":
                return handleZoomRequest();
            case "mainMenu":
                return handleMainMenuRequest();
            case "gameState":
                return handleGameStateRequest();
            default:
                return new ResponseData().setError("Unknown game state-related function: " + function);
        }
    }

    private Integer handleGameTickRequest() {
        return client.getTickCount();
    }

    private Integer handleZoomRequest() {
        return client.getScale();
    }

    private String handleMainMenuRequest() {
        log.info("Current game state: {}", client.getGameState());
        if (client.getGameState() != GameState.LOGIN_SCREEN) {
            log.warn("Main menu data requested but not in login screen.");
            return client.getGameState().name();
        }
        return client.getGameState().name();
    }

    private String handleGameStateRequest() {
        return client.getGameState().name();
    }
}