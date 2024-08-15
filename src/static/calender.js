document.addEventListener('DOMContentLoaded', function() {
    const calendarContainer = document.getElementById('calendar-container');
    const dateInput = document.getElementById('personal_leave');

    const firstDayOfWeek = parseInt(calendarContainer.getAttribute('data-first-day-of-week'), 10);
    const daysInMonth = parseInt(calendarContainer.getAttribute('data-days-in-month'), 10);

    // 用於儲存選中的時段
    const selectedSlots = [];

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

        const morningBtn = document.createElement('button');
        morningBtn.textContent = i.toString() + "/上";
        morningBtn.classList.add('morning');
        morningBtn.dataset.date = i;
        morningBtn.dataset.period = '上午';
        dateCell.appendChild(morningBtn);

        const afternoonBtn = document.createElement('button');
        afternoonBtn.textContent = i.toString() + "/下";
        afternoonBtn.classList.add('afternoon');
        afternoonBtn.dataset.date = i;
        afternoonBtn.dataset.period = '下午';
        dateCell.appendChild(afternoonBtn);

        calendarContainer.appendChild(dateCell);
    }

    // 处理按钮点击事件
    calendarContainer.addEventListener('click', function(event) {
        if (event.target.tagName === 'BUTTON') {
            const selectedDate = event.target.dataset.date;
            const selectedPeriod = event.target.dataset.period;
            const slot = `${selectedDate}/${selectedPeriod}`;

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

