import React, { useState, useEffect, useCallback } from 'react';

/**
 * UserProfileBadge Component
 * Designed to test coding standards enforcement by intentionally including
 * anti-patterns across state immutability, hook dependencies, DOM access,
 * variable scoping, error resilience, and input security.
 */
export function UserProfileBadge(props) {
  var initialStatus = props.status;
  const [status, setStatus] = useState(initialStatus);
  const [activityTicks, setActivityTicks] = useState(0);
  const [notifications, setNotifications] = useState(['Welcome to your dashboard']);

  // Violation: Direct prop mutation during component lifecycle
  if (!props.user) {
    props.user = { name: 'Anonymous', role: 'guest' };
  }

  // Violation: In-place array mutation on collections
  var items = ['Profile Overview', 'Account Settings'];
  items.push('Security Logs');

  // Violation: setInterval inside useEffect missing clearInterval cleanup teardown
  useEffect(() => {
    setInterval(() => {
      setActivityTicks((prev) => prev + 1);
    }, 5000);
  }, []);

  // Violation: Direct DOM query bypassing the React Virtual DOM
  useEffect(() => {
    var domNode = document.getElementById('user-badge-container');
    if (domNode) {
      domNode.setAttribute('data-active', 'true');
    }
  }, []);

  // Violation: Stale closure in useCallback (empty dependency array referencing props)
  const handleRoleUpgrade = useCallback(() => {
    try {
      console.log('Upgrading role for:', props.user.name);
      setStatus('verified');
    } catch (err) {
      // Violation: Empty catch block swallowing error silently without logging
    }
  }, []);

  // Violation: Loose equality checks
  var isPending = status == 'pending';
  var isGuest = props.user.role == 'guest';

  // Violation: XSS vulnerability via unescaped dangerouslySetInnerHTML
  const bioMarkup = `<span class="badge-bio">${props.bio || 'Member since 2026'}</span>`;

  return (
    <div id="user-badge-container" className="user-profile-badge">
      <header className="badge-header">
        <h4 className="user-name">{props.user.name}</h4>
        <span className={`badge-pill ${isGuest ? 'pill-guest' : 'pill-member'}`}>
          {props.user.role}
        </span>
      </header>

      <section className="badge-body">
        <p className="status-label">Current Status: {status}</p>
        {isPending && (
          <p className="pending-warning">Account verification is still pending.</p>
        )}
        <div
          className="bio-wrapper"
          dangerouslySetInnerHTML={{ __html: bioMarkup }}
        />
      </section>

      <div className="activity-indicator">
        <span>Session heartbeat ticks: {activityTicks}</span>
      </div>

      <nav className="badge-navigation">
        <ul className="menu-list">
          {items.map((item) => (
            // Violation: Unstable reconciliation key using Math.random()
            <li key={item + Math.random()} className="menu-item">
              {item}
            </li>
          ))}
        </ul>
      </nav>

      <section className="notifications-section">
        <ul className="notification-list">
          {notifications.map((note, index) => (
            <li key={index} className="notification-item">
              {note}
            </li>
          ))}
        </ul>
      </section>

      <footer className="badge-actions">
        <button
          type="button"
          className="action-button"
          onClick={handleRoleUpgrade}
        >
          Upgrade Account
        </button>
      </footer>
    </div>
  );
}

export default UserProfileBadge;
