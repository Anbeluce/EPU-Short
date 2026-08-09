import validators
import bleach
from bleach.css_sanitizer import CSSSanitizer
from datetime import datetime, timedelta, timezone
from sqlmodel import Session, select
from typing import Optional, List, Dict, Any

from app.models import Link, Note
from app.utils import generate_short_code, hash_password, validate_custom_code

def utcnow():
    return datetime.now()

def create_short_link(session: Session, url: str, custom_code: Optional[str] = None, expires_at: Optional[datetime] = None, is_admin: bool = False) -> Link:
    if not url.startswith(('http://', 'https://', 'ftp://')):
        url = 'https://' + url
    if not validators.url(url):
        raise ValueError("Invalid URL")
        
    code = custom_code
    if code:
        if not validate_custom_code(code, is_admin=is_admin):
            raise ValueError("Invalid custom code format")
        existing = session.exec(select(Link).where(Link.short_code == code)).first()
        if existing:
            raise ValueError("Code đã được sử dụng!")
    else:
        for _ in range(10):
            code = generate_short_code()
            if not session.exec(select(Link).where(Link.short_code == code)).first():
                break
        else:
            raise ValueError("Failed to generate a unique short code")
    link = Link(
        short_code=code,
        original_url=url,
        expires_at=expires_at
    )
    session.add(link)
    session.commit()
    session.refresh(link)
    return link

def get_link_by_code(session: Session, code: str) -> Optional[Link]:
    link = session.exec(select(Link).where(Link.short_code == code)).first()
    if not link or not link.is_active:
        return None
    if link.expires_at and link.expires_at < utcnow():
        return None
    return link

def increment_link_clicks(session: Session, link: Link):
    link.click_count += 1
    session.add(link)
    session.commit()

def create_note(session: Session, content: str, title: Optional[str] = None, custom_code: Optional[str] = None, password: Optional[str] = None, expires_at: Optional[datetime] = None, is_admin: bool = False) -> Note:
    # Sanitize HTML content
    allowed_tags = bleach.sanitizer.ALLOWED_TAGS.union({'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'span', 'br', 'strong', 'em', 'u', 's', 'ol', 'ul', 'li', 'a', 'img', 'blockquote', 'pre'})
    allowed_attributes = {
        **bleach.sanitizer.ALLOWED_ATTRIBUTES,
        'a': ['href', 'title', 'target'],
        'img': ['src', 'alt', 'width', 'height'],
        'span': ['style', 'class'],
        '*': ['style', 'class']
    }
    allowed_styles = ['color', 'background-color', 'text-align', 'font-size', 'font-family']
    
    css_sanitizer = CSSSanitizer(allowed_css_properties=allowed_styles)
    clean_content = bleach.clean(content, tags=allowed_tags, attributes=allowed_attributes, css_sanitizer=css_sanitizer)

    code = custom_code
    if code:
        if not validate_custom_code(code, is_admin=is_admin):
            raise ValueError("Invalid custom code format")
        existing = session.exec(select(Note).where(Note.short_code == code)).first()
        if existing:
            raise ValueError("Code đã được sử dụng!")
    else:
        for _ in range(10):
            code = generate_short_code()
            if not session.exec(select(Note).where(Note.short_code == code)).first():
                break
        else:
            raise ValueError("Failed to generate a unique short code")
    note = Note(
        short_code=code,
        title=title,
        content=clean_content,
        password_hash=hash_password(password) if password else None,
        expires_at=expires_at
    )
    session.add(note)
    session.commit()
    session.refresh(note)
    return note

def get_note_by_code(session: Session, code: str) -> Optional[Note]:
    note = session.exec(select(Note).where(Note.short_code == code)).first()
    if not note or not note.is_active:
        return None
    if note.expires_at and note.expires_at < utcnow():
        return None
    return note

def increment_note_views(session: Session, note: Note):
    note.view_count += 1
    session.add(note)
    session.commit()

def get_all_links(session: Session) -> List[Link]:
    return session.exec(select(Link).order_by(Link.created_at.desc())).all()

def edit_link(session: Session, link_id: int, original_url: str, short_code: str, expires_at: Optional[datetime] = None) -> Link:
    link = session.get(Link, link_id)
    if not link:
        raise ValueError("Link not found")
        
    if not validators.url(original_url):
        raise ValueError("Invalid URL")
        
    if short_code != link.short_code:
        if not validate_custom_code(short_code, is_admin=True):
            raise ValueError("Invalid custom code format")
        existing = session.exec(select(Link).where(Link.short_code == short_code)).first()
        if existing:
            raise ValueError("Code đã được sử dụng!")
        link.short_code = short_code

    link.original_url = original_url
    
    link.expires_at = expires_at
    
    session.add(link)
    session.commit()
    session.refresh(link)
    return link

def edit_note(session: Session, note_id: int, content: str, title: Optional[str] = None, short_code: Optional[str] = None, password: Optional[str] = None, expires_at: Optional[datetime] = None) -> Note:
    note = session.get(Note, note_id)
    if not note:
        raise ValueError("Note not found")
        
    if short_code and short_code != note.short_code:
        if not validate_custom_code(short_code, is_admin=True):
            raise ValueError("Invalid custom code format")
        existing = session.exec(select(Note).where(Note.short_code == short_code)).first()
        if existing:
            raise ValueError("Code đã được sử dụng!")
        note.short_code = short_code

    note.title = title
    
    # Sanitize HTML content
    allowed_tags = bleach.sanitizer.ALLOWED_TAGS.union({'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'span', 'br', 'strong', 'em', 'u', 's', 'ol', 'ul', 'li', 'a', 'img', 'blockquote', 'pre'})
    allowed_attributes = {
        **bleach.sanitizer.ALLOWED_ATTRIBUTES,
        'a': ['href', 'title', 'target'],
        'img': ['src', 'alt', 'width', 'height'],
        'span': ['style', 'class'],
        '*': ['style', 'class']
    }
    allowed_styles = ['color', 'background-color', 'text-align', 'font-size', 'font-family']
    css_sanitizer = CSSSanitizer(allowed_css_properties=allowed_styles)
    clean_content = bleach.clean(content, tags=allowed_tags, attributes=allowed_attributes, css_sanitizer=css_sanitizer)
    
    note.content = clean_content
    
    if password:
        note.password_hash = hash_password(password)
        
    if expires_at is not None:
        note.expires_at = expires_at
        
    session.add(note)
    session.commit()
    session.refresh(note)
    return note

def get_all_notes(session: Session) -> List[Note]:
    return session.exec(select(Note).order_by(Note.created_at.desc())).all()

def toggle_link_active(session: Session, link_id: int) -> Link:
    link = session.get(Link, link_id)
    if link:
        link.is_active = not link.is_active
        session.add(link)
        session.commit()
        session.refresh(link)
    return link

def toggle_note_active(session: Session, note_id: int) -> Note:
    note = session.get(Note, note_id)
    if note:
        note.is_active = not note.is_active
        session.add(note)
        session.commit()
        session.refresh(note)
    return note

def delete_link(session: Session, link_id: int):
    link = session.get(Link, link_id)
    if link:
        session.delete(link)
        session.commit()

def delete_note(session: Session, note_id: int):
    note = session.get(Note, note_id)
    if note:
        session.delete(note)
        session.commit()

def get_overview_stats(session: Session) -> Dict[str, Any]:
    links = session.exec(select(Link)).all()
    notes = session.exec(select(Note)).all()
    
    return {
        "total_links": len(links),
        "total_notes": len(notes),
        "total_clicks": sum(l.click_count for l in links),
        "total_views": sum(n.view_count for n in notes),
        "total_protected": sum(1 for l in links if l.password_hash) + sum(1 for n in notes if n.password_hash)
    }
