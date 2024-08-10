```java
import java.security.SecureRandom;

public class App {
    public static void main(String[] args) {
        SecureRandom secureRandom = new SecureRandom();
        int randomNumber = secureRandom.nextInt(100); // Gera um número aleatório entre 0 e 99 de forma segura
        System.out.println("Número aleatório: " + randomNumber);
    }
}
```