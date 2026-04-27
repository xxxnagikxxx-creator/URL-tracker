import { FormEvent, useEffect, useMemo, useRef, useState } from "react";
import {
  Activity,
  Clock3,
  ExternalLink,
  Link2,
  Loader2,
  LogOut,
  Plus,
  ShieldCheck,
  Trash2,
  UserRound,
} from "lucide-react";
import { api } from "./api";
import type { LinkCheck, LinkDetails, LinkSummary, TelegramAuthPayload, User } from "./types";

type LoadState = "idle" | "loading" | "ready" | "error";

const formatDate = (value: string) =>
  new Intl.DateTimeFormat("ru-RU", {
    day: "2-digit",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(value));

const getStatusClass = (statusCode: number) => {
  if (statusCode >= 200 && statusCode < 300) return "status ok";
  if (statusCode >= 300 && statusCode < 500) return "status warn";
  return "status bad";
};

const calculateUptime = (checks: LinkCheck[]) => {
  if (!checks.length) return 0;
  const healthyChecks = checks.filter((check) => check.status_code >= 200 && check.status_code < 400);
  return Math.round((healthyChecks.length / checks.length) * 100);
};

function AuthCard({ onLogin }: { onLogin: (user: User) => void }) {
  const widgetRef = useRef<HTMLDivElement | null>(null);
  const botUsername = import.meta.env.VITE_TELEGRAM_BOT_USERNAME ?? "testivecheckerbot";
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    if (!widgetRef.current) return;

    window.onTelegramAuth = async (payload: TelegramAuthPayload) => {
      setError("");
      setIsSubmitting(true);

      try {
        const user = await api.loginWithTelegram(payload);
        onLogin(user);
      } catch (error) {
        setError(error instanceof Error ? error.message : "Не удалось войти через Telegram");
      } finally {
        setIsSubmitting(false);
      }
    };

    widgetRef.current.innerHTML = "";
    const script = document.createElement("script");
    script.src = "https://telegram.org/js/telegram-widget.js?22";
    script.async = true;
    script.setAttribute("data-telegram-login", botUsername);
    script.setAttribute("data-size", "large");
    script.setAttribute("data-radius", "14");
    script.setAttribute("data-request-access", "write");
    script.setAttribute("data-onauth", "onTelegramAuth(user)");
    widgetRef.current.appendChild(script);

    return () => {
      delete window.onTelegramAuth;
    };
  }, [botUsername, onLogin]);

  return (
    <main className="auth-layout">
      <section className="hero-card">
        <div className="badge">
          <ShieldCheck size={18} />
          Cookie based auth
        </div>
        <h1>Live Checker</h1>
        <p>
          Красивый кабинет для мониторинга ссылок: добавляйте URL, смотрите историю проверок,
          uptime и скорость ответа.
        </p>
      </section>

      <section className="auth-card">
        <div>
          <p className="eyebrow">Вход</p>
          <h2>Войти через Telegram</h2>
          <p className="muted">Нажмите кнопку Telegram. Backend проверит подпись виджета и выдаст HttpOnly cookies.</p>
        </div>

        <div className="telegram-widget" ref={widgetRef} />

        {isSubmitting && (
          <div className="loading-box">
            <Loader2 className="spin" size={18} />
            Проверяем Telegram-профиль...
          </div>
        )}

        {error && <div className="error-box">{error}</div>}

        <p className="muted small">
          Используется бот @{botUsername}. Для production домен должен быть настроен в BotFather через /setdomain.
        </p>
      </section>
    </main>
  );
}

function MetricCard({ label, value, hint }: { label: string; value: string; hint: string }) {
  return (
    <article className="metric-card">
      <span>{label}</span>
      <strong>{value}</strong>
      <small>{hint}</small>
    </article>
  );
}

function Dashboard({ user, onLogout }: { user: User; onLogout: () => void }) {
  const [links, setLinks] = useState<LinkSummary[]>([]);
  const [selectedLink, setSelectedLink] = useState<LinkDetails | null>(null);
  const [url, setUrl] = useState("");
  const [state, setState] = useState<LoadState>("loading");
  const [error, setError] = useState("");

  const checks = selectedLink?.checks ?? [];
  const lastCheck = checks[checks.length - 1];

  const averageResponseTime = useMemo(() => {
    if (!checks.length) return "0 ms";
    const average = checks.reduce((sum, check) => sum + check.response_time, 0) / checks.length;
    return `${Math.round(average * 1000)} ms`;
  }, [checks]);

  const loadLinks = async () => {
    setState("loading");
    setError("");

    try {
      const data = await api.getLinks();
      setLinks(data.links);

      if (data.links.length > 0) {
        const details = await api.getLink(data.links[0].id);
        setSelectedLink(details);
      } else {
        setSelectedLink(null);
      }

      setState("ready");
    } catch (error) {
      setError(error instanceof Error ? error.message : "Не удалось загрузить ссылки");
      setState("error");
    }
  };

  useEffect(() => {
    void loadLinks();
  }, []);

  const addLink = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError("");

    try {
      const createdLink = await api.createLink(url);
      setUrl("");
      setLinks((current) => [{ id: createdLink.id, url: createdLink.url }, ...current]);
      setSelectedLink(createdLink);
    } catch (error) {
      setError(error instanceof Error ? error.message : "Не удалось добавить ссылку");
    }
  };

  const selectLink = async (linkId: number) => {
    setError("");

    try {
      setSelectedLink(await api.getLink(linkId));
    } catch (error) {
      setError(error instanceof Error ? error.message : "Не удалось открыть ссылку");
    }
  };

  const removeLink = async (linkId: number) => {
    setError("");

    try {
      await api.deleteLink(linkId);
      setLinks((current) => current.filter((link) => link.id !== linkId));

      if (selectedLink?.id === linkId) {
        setSelectedLink(null);
      }
    } catch (error) {
      setError(error instanceof Error ? error.message : "Не удалось удалить ссылку");
    }
  };

  const logout = async () => {
    await api.logout();
    onLogout();
  };

  return (
    <main className="dashboard">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon">
            <Activity size={22} />
          </div>
          <div>
            <strong>Live Checker</strong>
            <span>Uptime monitor</span>
          </div>
        </div>

        <form className="add-link" onSubmit={addLink}>
          <label>
            Новая ссылка
            <input
              type="url"
              value={url}
              onChange={(event) => setUrl(event.target.value)}
              placeholder="https://example.com"
              required
            />
          </label>
          <button className="primary-button">
            <Plus size={18} />
            Добавить
          </button>
        </form>

        <div className="links-list">
          {links.map((link) => (
            <button
              key={link.id}
              className={selectedLink?.id === link.id ? "link-row active" : "link-row"}
              onClick={() => void selectLink(link.id)}
            >
              <Link2 size={16} />
              <span>{link.url}</span>
            </button>
          ))}
        </div>

        <button className="ghost-button" onClick={() => void logout()}>
          <LogOut size={18} />
          Выйти
        </button>
      </aside>

      <section className="content">
        <header className="topbar">
          <div>
            <p className="eyebrow">Личный кабинет</p>
            <h1>Привет, {user.first_name}</h1>
          </div>
          <div className="user-pill">
            <UserRound size={18} />
            {user.username ? `@${user.username}` : user.telegram_id}
          </div>
        </header>

        {error && <div className="error-box">{error}</div>}

        {state === "loading" ? (
          <div className="empty-state">
            <Loader2 className="spin" size={28} />
            Загружаем ссылки...
          </div>
        ) : selectedLink ? (
          <>
            <section className="link-hero">
              <div>
                <p className="eyebrow">Selected URL</p>
                <h2>{selectedLink.url}</h2>
                <a href={selectedLink.url} target="_blank" rel="noreferrer">
                  Открыть сайт <ExternalLink size={16} />
                </a>
              </div>
              <button className="danger-button" onClick={() => void removeLink(selectedLink.id)}>
                <Trash2 size={18} />
                Удалить
              </button>
            </section>

            <section className="metrics-grid">
              <MetricCard label="Uptime" value={`${calculateUptime(checks)}%`} hint={`${checks.length} проверок`} />
              <MetricCard
                label="Последний статус"
                value={lastCheck ? String(lastCheck.status_code) : "Нет данных"}
                hint={lastCheck ? formatDate(lastCheck.created_at) : "Воркер еще не проверял"}
              />
              <MetricCard label="Средний ответ" value={averageResponseTime} hint="По сохраненной истории" />
            </section>

            <section className="history-card">
              <div className="section-title">
                <Clock3 size={18} />
                История проверок
              </div>

              {checks.length ? (
                <div className="checks-table">
                  {checks
                    .slice()
                    .reverse()
                    .map((check) => (
                      <div className="check-row" key={check.id}>
                        <span className={getStatusClass(check.status_code)}>{check.status_code}</span>
                        <span>{Math.round(check.response_time * 1000)} ms</span>
                        <span>{formatDate(check.created_at)}</span>
                      </div>
                    ))}
                </div>
              ) : (
                <div className="empty-state compact">Проверок пока нет. ARQ worker добавит их каждые 10 минут.</div>
              )}
            </section>
          </>
        ) : (
          <div className="empty-state">
            <Link2 size={32} />
            Добавьте первую ссылку, чтобы начать мониторинг.
          </div>
        )}
      </section>
    </main>
  );
}

export default function App() {
  const [user, setUser] = useState<User | null>(null);
  const [isBooting, setIsBooting] = useState(true);

  useEffect(() => {
    api
      .getCurrentUser()
      .then(setUser)
      .catch(() => setUser(null))
      .finally(() => setIsBooting(false));
  }, []);

  if (isBooting) {
    return (
      <div className="boot-screen">
        <Loader2 className="spin" size={32} />
      </div>
    );
  }

  return user ? <Dashboard user={user} onLogout={() => setUser(null)} /> : <AuthCard onLogin={setUser} />;
}
