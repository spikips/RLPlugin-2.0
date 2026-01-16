package net.runelite.client.plugins.asd;

import java.util.Map;

public interface RequestHandler {
    Object handle(String function, Map<String, Object> params);
}