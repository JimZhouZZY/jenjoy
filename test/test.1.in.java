import java.util.List;

public class ExampleClass {

    public String processString(String input) {
        if (input == null) {
            return null;
        }
        return input.toUpperCase();
    }

    @Override
    public String toString() {
        return "ExampleClass{" +
                "version=1.0" +
                '}';
    }

    public double calculateAverage(List<Double> numbers) {
        if (numbers == null || numbers.isEmpty()) {
            throw new IllegalArgumentException("Error calculating average: List is null or empty");
        }
        
        double sum = 0;
        for (Double num : numbers) {
            sum += num;
        }
        return sum / numbers.size();
    }
}
