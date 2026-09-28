document.addEventListener(
    "DOMContentLoaded",
    () => {

        const textareas =
            document.querySelectorAll(
                "textarea[maxlength]"
            );


        textareas.forEach(
            (textarea) => {

                const counter =
                    document.createElement(
                        "small"
                    );


                counter.className =
                    "muted";


                textarea.insertAdjacentElement(
                    "afterend",
                    counter
                );


                const updateCounter =
                    () => {

                        counter.textContent =
                            `${textarea.value.length}/${textarea.maxLength} characters`;

                    };


                textarea.addEventListener(
                    "input",
                    updateCounter
                );


                updateCounter();

            }
        );

    }
);