package com.game.fantasyplanetadventure.server;

import com.almasb.common.encryption.Account;
import java.io.Serializable;

public class GameAccount extends Account {
    protected GameAccount(String username, String password, String key) {
        super(username, password, key);
    }
}
