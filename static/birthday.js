(function () {
    'use strict';

    // 页面加载时获取初始计数
    fetchCountAndUpdate();

    function addHeartIcon(count) {
        var h2Element = document.querySelector('h2');
        if (h2Element && !h2Element.querySelector('span.heart-icon')) {
            var heartIcon = document.createElement('span');
            heartIcon.innerHTML = '♥';
            heartIcon.classList.add('heart-icon');
            heartIcon.style.cursor = 'pointer';
            heartIcon.style.fontSize = '24px';
            heartIcon.style.marginLeft = '10px';
            heartIcon.title = '点击庆祝生日！'; // 悬浮提示

            var countSpan = document.createElement('span');
            countSpan.classList.add('count-display');
            countSpan.style.marginLeft = '5px';
            countSpan.textContent = '(0)';

            var fontTag = h2Element.querySelector('font');
            if (fontTag) {
                fontTag.appendChild(heartIcon);
                fontTag.appendChild(countSpan);
            } else {
                h2Element.appendChild(heartIcon);
                h2Element.appendChild(countSpan);
            }

            heartIcon.addEventListener('click', function () {
                // 点击事件处理
                fetch('/birthday_api/count', {
                    method: 'POST'
                })
                    .then(response => response.json())
                    .then(data => {
                        var count = data.count; // 假设返回的数据中有一个 count 字段
                        var message = data.message;
                        updateHeart(count);
                        celebrateBirthday(count);
                        updateCountDisplay(count);
                        showToast(message);
                    })
                    .catch(error => console.error('Error:', error));
            });
            // 添加悬浮窗元素
            var toastDiv = document.createElement('div');
            toastDiv.classList.add('toast-message');
            toastDiv.style.position = 'fixed';
            toastDiv.style.top = '20px'; // 放置在顶部
            toastDiv.style.left = '50%';
            toastDiv.style.transform = 'translateX(-50%)';
            toastDiv.style.backgroundColor = 'rgba(25, 118, 210, 0.9)'; // 深蓝色背景
            toastDiv.style.color = '#FFFFFF'; // 白色文字
            toastDiv.style.padding = '10px 20px';
            toastDiv.style.borderRadius = '5px';
            toastDiv.style.display = 'none';
            toastDiv.style.zIndex = '1000'; // 确保在最上层
            toastDiv.style.maxWidth = '90%'; // 最大宽度
            toastDiv.style.minWidth = '300px'; // 最小宽度
            toastDiv.style.fontSize = '16px'; // 字体大小
            toastDiv.style.textAlign = 'center';
            document.body.appendChild(toastDiv);

            // 媒体查询，适应小屏幕
            var styleSheet = document.createElement('style')
            styleSheet.type = 'text/css'
            styleSheet.innerText = `
            @media screen and (max-width: 600px) {
                .toast-message {
                    font-size: 14px; // 小屏幕上的字体大小
                    padding: 8px 15px; // 小屏幕上的内边距
                }
            }`;
            document.head.appendChild(styleSheet);
        }
    }

    // // 使用 MutationObserver 监听 DOM 变化
    // var observer = new MutationObserver(function (mutations) {
    //     mutations.forEach(function (mutation) {
    //         if (mutation.addedNodes.length) {
    //             fetchCountAndUpdate();
    //         }
    //     });
    // });

    observer.observe(document.body, { childList: true, subtree: true });

    // 获取计数并更新界面
    function fetchCountAndUpdate() {
        fetch('/birthday_api/count')
            .then(response => response.json())
            .then(data => {
                var count = data.count;
                addHeartIcon(count);
                updateHeart(count);
                updateCountDisplay(count);
            })
            .catch(error => console.error('Error:', error));
    }
})();

// 更新计数显示
function updateCountDisplay(count) {
    var countDisplay = document.querySelector('.count-display');
    if (countDisplay) {
        countDisplay.textContent = '(' + count + ')';
    }
}

// 根据返回的数字更新心形图标的颜色
function updateHeart(count) {
    var heartIcon = document.querySelector('span.heart-icon');
    if (heartIcon) {
        heartIcon.style.color = getColorForCount(count);
    }
}

// 根据计数获取颜色
function getColorForCount(count) {
    // 定义颜色从灰色到红色的渐变
    var startColor = { r: 128, g: 128, b: 128 }; // 灰色
    var endColor = { r: 255, g: 0, b: 0 }; // 红色
    var maxCount = 52; // 定义最大计数，用于颜色变化

    // 计算颜色比例
    var ratio = Math.min(count / maxCount, 1);

    // 计算新颜色值
    var newColor = {
        r: Math.round(startColor.r + ratio * (endColor.r - startColor.r)),
        g: Math.round(startColor.g + ratio * (endColor.g - startColor.g)),
        b: Math.round(startColor.b + ratio * (endColor.b - startColor.b))
    };

    return `rgb(${newColor.r}, ${newColor.g}, ${newColor.b})`;
}

// 庆祝生日的表达
function celebrateBirthday(count) {
    if (count % 10 === 0) { // 每当计数是 10 的倍数时显示庆祝信息
        alert('🎉 生日快乐！已有 ' + count + ' 人庆祝！🎉');
    }
}

// 显示悬浮窗消息
function showToast(message) {
    var toast = document.querySelector('.toast-message');
    if (toast) {
        toast.textContent = message;
        toast.style.display = 'block';

        // 消息显示后自动消失
        setTimeout(function () {
            toast.style.display = 'none';
        }, 2000); // 3秒后消失
    }
}