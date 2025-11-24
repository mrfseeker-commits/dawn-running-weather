// 새벽런닝 날씨 앱 메인 JavaScript

// 페이지 로드 시 실행
document.addEventListener('DOMContentLoaded', function() {
    console.log('새벽런닝 날씨 앱 로드 완료');

    // 다크모드 초기화
    initTheme();

    // 현재 시간 표시 (필요시)
    updateCurrentTime();
    setInterval(updateCurrentTime, 60000); // 1분마다 업데이트

    // 전체 업데이트 버튼
    const updateAllBtn = document.getElementById('update-all-btn');
    if (updateAllBtn) {
        updateAllBtn.addEventListener('click', updateAllWeather);
    }
});

// 다크모드 관리
function initTheme() {
    // localStorage에서 테마 가져오기
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);

    // 토글 버튼 이벤트 리스너
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', toggleTheme);
    }
}

function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';

    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);

    console.log('테마 변경:', newTheme);
}

// 현재 시간 업데이트
function updateCurrentTime() {
    const now = new Date();
    const timeString = now.toLocaleTimeString('ko-KR', {
        hour: '2-digit',
        minute: '2-digit'
    });

    const timeElements = document.querySelectorAll('.current-time');
    timeElements.forEach(el => {
        el.textContent = timeString;
    });
}

// Alert 자동 닫기
setTimeout(function() {
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(alert => {
        const bsAlert = new bootstrap.Alert(alert);
        bsAlert.close();
    });
}, 5000); // 5초 후 자동 닫기

// 유틸리티 함수들
const utils = {
    // 날짜 포맷팅
    formatDate: function(date) {
        return new Intl.DateTimeFormat('ko-KR', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        }).format(date);
    },

    // 기온에 따른 색상 반환
    getTempColor: function(temp) {
        if (temp >= 25) return 'text-danger';
        if (temp >= 15) return 'text-warning';
        if (temp >= 5) return 'text-success';
        if (temp >= 0) return 'text-primary';
        return 'text-info';
    },

    // 강수확률에 따른 뱃지 색상
    getPrecipBadgeClass: function(precip) {
        if (precip >= 60) return 'bg-danger';
        if (precip >= 40) return 'bg-warning';
        if (precip >= 20) return 'bg-info';
        return 'bg-secondary';
    }
};

// 전체 날씨 업데이트
async function updateAllWeather(e) {
    e.preventDefault();

    const btn = document.getElementById('update-all-btn');
    const icon = btn.querySelector('i');
    const originalText = btn.innerHTML;

    if (!confirm('전체 지역의 날씨 정보를 업데이트하시겠습니까?\n(크롤링에 시간이 소요될 수 있습니다)')) {
        return;
    }

    // 로딩 상태로 변경
    icon.classList.remove('bi-arrow-clockwise');
    icon.classList.add('bi-hourglass-split');
    btn.classList.add('disabled');
    btn.innerHTML = '<i class="bi bi-hourglass-split"></i> 업데이트 중...';

    try {
        const response = await fetch('/api/update_all_weather', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || '업데이트 실패');
        }

        alert(data.message);

        // 페이지 새로고침
        window.location.reload();

    } catch (error) {
        alert('날씨 업데이트 중 오류가 발생했습니다: ' + error.message);

        // 원래 상태로 복구
        btn.innerHTML = originalText;
        btn.classList.remove('disabled');
    }
}

// 전역으로 사용 가능하도록 설정
window.weatherApp = {
    utils: utils,
    updateAllWeather: updateAllWeather
};
