module com.game.fantasyplanetadventure {
    requires javafx.controls;
    requires javafx.fxml;

    requires com.almasb.fxgl.all;
    requires almasb.lib;

    opens com.game.fantasyplanetadventure.client to javafx.fxml;
    exports com.game.fantasyplanetadventure.client;
}