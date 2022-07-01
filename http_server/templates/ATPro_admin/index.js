const themeCookieName = 'KootnetThemeCookie'
const themeDark = 'dark'
const themeLight = 'light'

const body = document.getElementsByTagName('body')[0]

const html_loading = '<div class="row"><div class="col-12 col-m-12 col-sm-12">' +
        '<div class="card" style="width: 100vw;"><div class="card-content">' +
        '<h1><i class="fas fa-hourglass-half"></i> Loading ...</h1></div></div></div></div>'

function setCookie(cname, cvalue, exdays) {
  let d = new Date()
  d.setTime(d.getTime() + (exdays * 24 * 60 * 60 * 1000))
  let expires = "expires="+d.toUTCString()
  document.cookie = cname + "=" + cvalue + ";" + expires + ";path=/"
}

function getCookie(cname) {
  let name = cname + "="
  let ca = document.cookie.split(';')
  for(let i = 0; i < ca.length; i++) {
    let c = ca[i];
    while (c.charAt(0) == ' ') {
      c = c.substring(1)
    }
    if (c.indexOf(name) == 0) {
      return c.substring(name.length, c.length)
    }
  }
  return ""
}

loadTheme()

function loadTheme() {
	let theme = getCookie(themeCookieName)
	body.classList.add(theme === "" ? themeDark : theme)
}

function switchTheme() {
	if (body.classList.contains(themeLight)) {
		body.classList.remove(themeLight)
		body.classList.add(themeDark)
		setCookie(themeCookieName, themeDark, 14)
	} else {
		body.classList.remove(themeDark)
		body.classList.add(themeLight)
		setCookie(themeCookieName, themeLight, 14)
	}
}

function collapseSidebar() {
	body.classList.toggle('sidebar-expand')
}

window.onclick = function(event) {
	openCloseDropdown(event);
	if (!event.target.matches('.sidebar-stay-on')) {
		if (window.innerWidth < 601) {
			body.classList.remove('sidebar-expand')
		}
	}
}

function closeAllDropdown() {
	let dropdowns = document.getElementsByClassName('dropdown-expand')
	for (let i = 0; i < dropdowns.length; i++) {
		dropdowns[i].classList.remove('dropdown-expand')
	}
}

function openCloseDropdown(event) {
	if (!event.target.matches('.dropdown-toggle')) {
		// 
		// Close dropdown when click out of dropdown menu
		// 
		closeAllDropdown()
	} else {
		let toggle = event.target.dataset.toggle
		let content = document.getElementById(toggle)
		if (content.classList.contains('dropdown-expand')) {
			closeAllDropdown()
		} else {
			closeAllDropdown()
			content.classList.add('dropdown-expand')
		}
	}
}

function SelectNav(nav_location, skip_menu_select=false) {
	document.getElementById("main-page-view").innerHTML = html_loading;

	if (typeof refresh_timer !== 'undefined') {
		clearTimeout(refresh_timer);
	}

	if (skip_menu_select === false) {
		SelectActiveMainMenu(nav_location);
	} else {
		UnSelectAllMenus();
	}

	jQuery("#main-page-view").load("/atpro/" + nav_location);
}

function SelectActiveMainMenu(nav_location) {
	UnSelectAllMenus();
	document.getElementById(nav_location).classList.add("active");
}

function UnSelectAllMenus() {
	document.getElementById("sensor-dashboard").classList.remove("active");
	document.getElementById("sensor-readings-base").classList.remove("active");
	document.getElementById("sensor-notes").classList.remove("active");
	document.getElementById("sensor-graphing-db").classList.remove("active");
	document.getElementById("sensor-graphing-live").classList.remove("active");
	document.getElementById("sensor-rm").classList.remove("active");
	document.getElementById("mqtt-subscriber-view-data-stream").classList.remove("active");
	document.getElementById("sensor-checkin-view").classList.remove("active");
	document.getElementById("sensor-settings").classList.remove("active");
}

function select_all_sensor_checkboxes() {
	if (document.getElementById('select-all-checkboxes').checked) {
		jQuery("div[id=sensor-checkboxes] input:checkbox").prop('checked', true);
	} else {
		jQuery("div[id=sensor-checkboxes] input:checkbox").prop('checked', false);
	}
}

function CheckNotificationsAsync() {
	let notification_count_xmlHttp = new XMLHttpRequest();
	notification_count_xmlHttp.onreadystatechange = function() {
		if (notification_count_xmlHttp.readyState === 4 && notification_count_xmlHttp.status === 200)
			if (notification_count_xmlHttp.responseText === "0") {
				document.getElementById("notification-count").style.display = "none";
			} else {
				document.getElementById("notification-count").style.display = "inline-block";
				document.getElementById("notification-count").innerText = notification_count_xmlHttp.responseText;
			}
	}

	let notification_msgs_xmlHttp = new XMLHttpRequest();
	notification_msgs_xmlHttp.onreadystatechange = function() {
		if (notification_msgs_xmlHttp.readyState === 4 && notification_msgs_xmlHttp.status === 200)
			if (notification_msgs_xmlHttp.responseText !== "") {
				document.getElementById("notification-content").innerHTML = notification_msgs_xmlHttp.responseText;
			} else {
				document.getElementById("notification-content").innerHTML = "";
			}
	}

	notification_count_xmlHttp.open("GET", "/atpro/get-notification-count", true); // true for asynchronous
	notification_msgs_xmlHttp.open("GET", "/atpro/get-notification-messages", true); // true for asynchronous
	notification_count_xmlHttp.send(null);
	notification_msgs_xmlHttp.send(null);
}

function NotificationConfirmAction(prompt_text, command_url) {
	let r = confirm(prompt_text);
	if (r === true) {
		window.location = command_url
	}
}

function NotificationOkay(prompt_text, command_url) {
	alert(prompt_text);
}

function UpdateHiddenInputButtonPress(button_type) {
        document.getElementById("button_function").value = button_type;
        document.getElementById("button_function_form").submit()
    }
