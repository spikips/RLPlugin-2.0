package net.runelite.client.plugins.asd;

import com.google.inject.Binder;
import com.google.inject.Module;
import com.google.inject.Singleton;

public class AsdModule implements Module {
    @Override
    public void configure(Binder binder) {
        binder.bind(PlayerHandler.class).in(Singleton.class);
        binder.bind(EntityHandler.class).in(Singleton.class);
        binder.bind(WorldHandler.class).in(Singleton.class);
        binder.bind(GameStateHandler.class).in(Singleton.class);
        binder.bind(InterfaceHandler.class).in(Singleton.class);
    }
}