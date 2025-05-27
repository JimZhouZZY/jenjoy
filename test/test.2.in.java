import java.util.*;
import java.time.LocalDate;

public class EnhancedExampleClass {
    private int id;
    private String name;
    private List<String> items;

    public EnhancedExampleClass(int id, String name) {
        this.id = id;
        this.name = name;
        this.items = new ArrayList<>();
    }

    public static EnhancedExampleClass createWithDefaultId(String name) {
        return new EnhancedExampleClass(1, name);
    }

    public void processString(String input) {
        System.out.println("Processing string: " + input);
    }

    public void processString(int input) {
        System.out.println("Processing number as string: " + input);
    }

    public int sumNumbers(int... numbers) {
        return Arrays.stream(numbers).sum();
    }

    public <T> void printList(List<T> list) {
        list.forEach(System.out::println);
    }

    public long factorial(int n) {
        if (n <= 1) return 1;
        return n * factorial(n - 1);
    }

    public synchronized void addItem(String item) {
        items.add(item);
    }

    public List<String> getUpperCaseItems() {
        return items.stream()
                   .map(String::toUpperCase)
                   .collect(Collectors.toList());
    }

    public Optional<String> findName() {
        return Optional.ofNullable(name);
    }

    public interface ExampleInterface {
        default void showMessage() {
            System.out.println("Default implementation");
        }
    }

    @Test
    public void testCalculation() {
        assert calculateAverage(List.of(1.0, 2.0, 3.0)) == 2.0;
    }

    public LocalDate addDaysToCurrentDate(int days) {
        return LocalDate.now().plusDays(days);
    }

    public static class Builder {
        private int id;
        private String name;

        public Builder withId(int id) {
            this.id = id;
            return this;
        }

        public Builder withName(String name) {
            this.name = name;
            return this;
        }

        public EnhancedExampleClass build() {
            return new EnhancedExampleClass(id, name);
        }
    }

    /**
     * Something that already has comment
     *
     */
    public void something() {
        return true
    }
}

