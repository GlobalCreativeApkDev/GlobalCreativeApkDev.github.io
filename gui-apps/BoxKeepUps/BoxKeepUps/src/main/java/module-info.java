module com.game.boxkeepups {
    requires javafx.controls;
    requires javafx.fxml;

    requires com.almasb.fxgl.all;

    opens com.game.boxkeepups to javafx.fxml;
    exports com.game.boxkeepups;
}