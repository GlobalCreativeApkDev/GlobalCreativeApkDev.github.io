package com.game.fantasyplanetadventure.common.minigames;

import java.io.Serializable;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;
import java.util.Objects;

public class Minigame implements Serializable, Cloneable {
    /**
     * This class contains attributes of a minigame in this game.
     * @author GlobalCreativeApkDev
     * */

    // Class attributes
    public static final ArrayList<String> POSSIBLE_NAMES =
            new ArrayList<>(List.of("BOX EATS PLANTS", "MATCH WORD PUZZLE", "MATCH-3 GAME"));
    private String name;
    private boolean alreadyPlayed;

    public Minigame(String name) {
        this.name = POSSIBLE_NAMES.contains(name) ? name : POSSIBLE_NAMES.get(0);
        alreadyPlayed = false;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public boolean isAlreadyPlayed() {
        return alreadyPlayed;
    }

    public void setAlreadyPlayed(boolean alreadyPlayed) {
        this.alreadyPlayed = alreadyPlayed;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        Minigame minigame = (Minigame) o;
        return alreadyPlayed == minigame.alreadyPlayed && Objects.equals(name, minigame.name);
    }

    @Override
    public int hashCode() {
        return Objects.hash(name, alreadyPlayed);
    }

    public Minigame clone() throws CloneNotSupportedException {
        return (Minigame) super.clone();
    }

    public boolean reset() {
        Date date = new Date();
        if (alreadyPlayed && date.getHours() > 0) {
            alreadyPlayed = false;
            return true;
        }
        return false;
    }
}
