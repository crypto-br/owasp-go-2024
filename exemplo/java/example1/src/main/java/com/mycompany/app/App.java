import java.security.SecureRandom;

    public class App {
        public static void main(String[] args) {
            SecureRandom secureRandom = new SecureRandom();
            int randomNumber = secureRandom.nextInt(100); // Gera um número aleatório de 0 a 99 de forma segura
            System.out.println(randomNumber);
        }
    }
    