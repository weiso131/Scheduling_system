document.addEventListener('DOMContentLoaded', function() {
    const calendarContainer = document.getElementById('calendar-container');
    const dateInput = document.getElementById('personal_leave');
    

    const firstDayOfWeek = parseInt(calendarContainer.getAttribute('data-first-day-of-week'), 10);
    const daysInMonth = parseInt(calendarContainer.getAttribute('data-days-in-month'), 10);
    let originalChoiceToken = calendarContainer.getAttribute('data-original-select-days').replace(/'/g, '"');

    // 用於儲存選中的時段
    const selectedSlots = JSON.parse(originalChoiceToken);
    let originCounter = 0;
    const periodName = ["/上", "/下"]

    // 生成日曆
    for (let i = 0; i < firstDayOfWeek; i++) {
        const emptyCell = document.createElement('div');
        emptyCell.classList.add('date-cell');
        calendarContainer.appendChild(emptyCell);
    }

    for (let i = 1; i <= daysInMonth; i++) {
        const dateCell = document.createElement('div');
        dateCell.classList.add('date-cell');

        const dateLabel = document.createElement('span');
        dateCell.appendChild(dateLabel);

        

        for (let j = 0;j < 2;j++) {
            const Btn = document.createElement('button');
            Btn.textContent = i.toString() + periodName[j];
            Btn.classList.add('periods');
            Btn.dataset.data = i.toString() + periodName[j] + "午";
            dateCell.appendChild(Btn);
            if (originCounter < selectedSlots.length && Btn.dataset.data == selectedSlots[originCounter]) {
                originCounter++;
                Btn.classList.add('selected');
            }
        }

        calendarContainer.appendChild(dateCell);
    }
    dateInput.value = selectedSlots.join(', ');
    // 处理按钮点击事件
    calendarContainer.addEventListener('click', function(event) {
        if (event.target.tagName === 'BUTTON') {
            const slot = event.target.dataset.data;

            // 如果已經選中，取消選擇
            if (event.target.classList.contains('selected')) {
                event.target.classList.remove('selected');
                const index = selectedSlots.indexOf(slot);
                if (index > -1) {
                    selectedSlots.splice(index, 1);
                }
            } else {
                // 如果未選中，添加到選中的時段
                event.target.classList.add('selected');
                selectedSlots.push(slot);
            }

            // 更新輸入框中的值
            dateInput.value = selectedSlots.join(', ');
        }
    });
});

