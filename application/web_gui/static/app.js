document.addEventListener("DOMContentLoaded", () => {
    const counterValueElement = document.getElementById("counter-value");
    const incrementButton = document.getElementById("increment-button");
    const decrementButton = document.getElementById("decrement-button");

    // Fetch the current counter value from the backend
    async function fetchCounter() {
        try {
            const response = await fetch("/get_data");
            const data = await response.json();
            counterValueElement.textContent = data.counter;
        } catch (error) {
            console.error("Failed to fetch counter value:", error);
        }
    }

    // Update the counter value in the backend
    async function updateCounter(newCounterValue) {
        try {
            const response = await fetch("/update_data", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ counter: newCounterValue }),
            });

            if (response.ok) {
                counterValueElement.textContent = newCounterValue;
            } else {
                console.error("Failed to update counter value.");
            }
        } catch (error) {
            console.error("Failed to update counter value:", error);
        }
    }

    // Increment button click handler
    incrementButton.addEventListener("click", () => {
        const currentValue = parseInt(counterValueElement.textContent, 10);
        const newValue = currentValue + 1;
        updateCounter(newValue);
    });

    // Decrement button click handler
    decrementButton.addEventListener("click", () => {
        const currentValue = parseInt(counterValueElement.textContent, 10);
        const newValue = currentValue - 1;
        updateCounter(newValue);
    });

    // Initial fetch of counter value
    fetchCounter();
});
